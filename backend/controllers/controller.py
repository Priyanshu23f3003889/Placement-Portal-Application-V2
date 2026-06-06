from datetime import datetime

from database.models import *
from flask import current_app as app
from flask import jsonify, render_template, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

jwt = JWTManager(app)


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email").strip()
    password = data.get("password")
    role_name = data.get("role")

    if not email or not password or not role_name:
        return jsonify({"message": "Email, password and role are required"}), 400

    user_exists = db.session.scalar(db.select(User).where(User.email == email))

    if user_exists:
        return jsonify({"message": "User already exists"}), 400

    role = db.session.scalar(db.select(Role).where(Role.name == role_name))
    if not role:
        return jsonify({"message": "Invalid role"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, roleid=role.id)
    db.session.add(new_user)
    db.session.flush()

    if role_name == "STUDENT":
        name = data.get("name")
        branch = data.get("branch")
        cgpa = data.get("cgpa")
        resumeUrl = data.get("resumeUrl")

        if not name or not branch or cgpa is None:
            return jsonify({"message": "Missing student details"}), 400

        new_student = Student(
            userId=new_user.id,
            name=name,
            branch=Branch[branch],
            cgpa=float(cgpa),
            resumeUrl=resumeUrl,
        )
        db.session.add(new_student)

    elif role_name == "COMPANY":
        name = data.get("name")
        hrContact = data.get("hrContact")
        website = data.get("website")

        if not name or not hrContact or not website:
            return jsonify({"message": "Missing company details"}), 400

        new_company = Company(
            userId=new_user.id, name=name, hrContact=hrContact, website=website
        )
        db.session.add(new_company)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email").strip()
    password = data.get("password")

    user = db.session.scalar(db.select(User).where(User.email == email))

    if user and check_password_hash(user.password, password):
        if not user.isActive:
            return jsonify({"message": "Account is blocked"}), 403

        additional_claims = {"role": user.role.name}
        access_token = create_access_token(
            identity=str(user.id), additional_claims=additional_claims
        )

        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid email or password"}), 401


@app.route("/api/admin/companies", methods=["GET"])
@jwt_required()
def adminCompanies():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        companies = (
            db.session.execute(db.select(Company).order_by(Company.isApproved))
            .scalars()
            .all()
        )
        companies_data = [
            {
                "id": c.id,
                "name": c.name,
                "hrContact": c.hrContact,
                "website": c.website,
                "isApproved": c.isApproved,
            }
            for c in companies
        ]
        return jsonify(companies_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/admin/companies/<int:company_id>", methods=["DELETE"])
@jwt_required()
def deleteCompany(company_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name != "ADMIN":
        return jsonify({"message": "Access Denied"}), 403

    company = db.session.scalar(db.select(Company).where(Company.id == company_id))
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company_user = db.session.scalar(db.select(User).where(User.id == company.userId))
    company_drives = company.drives

    try:
        for drive in company.drives:
            for application in drive.applications:
                db.session.delete(application)
            for placement in drive.placements:
                db.session.delete(placement)
            db.session.delete(drive)

        for placement in company.placements:
            db.session.delete(placement)

        db.session.delete(company)
        db.session.delete(company_user)
        db.session.commit()
        return jsonify({"message": "Company deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/admin/companies/<int:company_id>/toggle-approval", methods=["PATCH"])
@jwt_required()
def toggleCompanyApproval(company_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name != "ADMIN":
        return jsonify({"message": "Access Denied"}), 403

    company = db.session.scalar(db.select(Company).where(Company.id == company_id))
    if not company:
        return jsonify({"message": "Company not found"}), 404

    try:
        company.isApproved = not company.isApproved
        if not company.isApproved:
            for drive in company.drives:
                if drive.status == DriveStatus.APPROVED:
                    drive.status = DriveStatus.PENDING
        db.session.commit()
        return jsonify(
            {
                "message": "Company approval status updated",
                "isApproved": company.isApproved,
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/admin/students/<int:student_id>/toggle-approval", methods=["PATCH"])
@jwt_required()
def toggleStudnetApproval(student_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name != "ADMIN":
        return jsonify({"message": "Access Denied"}), 403

    student = db.session.scalar(db.select(Student).where(Student.id == student_id))
    if not student:
        return jsonify({"message": "Student not found"}), 404

    try:
        student.user.isActive = not student.user.isActive
        db.session.commit()
        return jsonify(
            {
                "message": "Company approval status updated",
                "isApproved": student.user.isActive,
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/admin/applications", methods=["GET"])
@jwt_required()
def adminApplications():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        applications = (
            db.session.execute(
                db.select(Application).order_by(Application.applicationDate.desc())
            )
            .scalars()
            .all()
        )
        apps_data = [
            {
                "id": a.id,
                "name": a.student.name,
                "driveId": a.driveId,
                "jobTitle": a.drive.jobTitle,
                "resumeUrl": a.student.resumeUrl,
                "status": a.status.value if hasattr(a.status, "value") else a.status,
            }
            for a in applications
        ]
        return jsonify(apps_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/admin/students", methods=["GET"])
@jwt_required()
def adminStudents():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        students = (
            db.session.execute(db.select(Student).order_by(Student.name))
            .scalars()
            .all()
        )
        students_data = [
            {
                "id": s.id,
                "name": s.name,
                "resumeUrl": s.resumeUrl,
                "cgpa": s.cgpa,
                "isApproved": s.user.isActive,
                "branch": s.branch,
            }
            for s in students
        ]
        return jsonify(students_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/admin/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def deleteStudent(student_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name != "ADMIN":
        return jsonify({"message": "Access Denied"}), 403

    student = db.session.scalar(db.select(Student).where(Student.id == student_id))
    if not student:
        return jsonify({"message": "Student not found"}), 404

    try:
        for application in student.applications:
            db.session.delete(application)
        for placement in student.placements:
            db.session.delete(placement)

        db.session.delete(student)
        db.session.delete(student.user)
        db.session.commit()
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


def update_expired_drives_status():
    try:
        now = datetime.now()
        expired_drives = (
            db.session.execute(
                db.select(PlacementDrive).where(
                    PlacementDrive.deadline < now,
                    PlacementDrive.status != DriveStatus.CLOSED,
                )
            )
            .scalars()
            .all()
        )

        for drive in expired_drives:
            drive.status = DriveStatus.CLOSED

        if expired_drives:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating expired drives: {e}")


@app.route("/api/admin/Drives", methods=["GET"])
@jwt_required()
def adminDrives():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        update_expired_drives_status()
        drives = (
            db.session.execute(db.select(PlacementDrive).order_by(PlacementDrive.id))
            .scalars()
            .all()
        )
        drives_data = [
            {
                "id": d.id,
                "jobTitle": d.jobTitle,
                "jobDescription": d.jobDescription,
                "companyName": d.company.name if d.company else "",
                "branch": d.branch.value if hasattr(d.branch, "value") else d.branch,
                "cgpa": d.cgpa,
                "deadline": d.deadline.strftime("%Y-%m-%d %H:%M:%S")
                if d.deadline
                else None,
                "status": d.status.value if hasattr(d.status, "value") else d.status,
            }
            for d in drives
        ]
        return jsonify(drives_data), 200
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/admin/drives/<int:drive_id>/toggle-approval", methods=["PATCH"])
@jwt_required()
def toggleDriveApproval(drive_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name != "ADMIN":
        return jsonify({"message": "Access Denied"}), 403

    drive = db.session.scalar(
        db.select(PlacementDrive).where(PlacementDrive.id == drive_id)
    )
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    try:
        if drive.status == DriveStatus.PENDING:
            drive.status = DriveStatus.APPROVED
        elif drive.status == DriveStatus.APPROVED:
            drive.status = DriveStatus.PENDING

        db.session.commit()
        return jsonify(
            {
                "message": "Drive approval status updated",
                "status": drive.status.value
                if hasattr(drive.status, "value")
                else drive.status,
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/student", methods=["GET"])
@jwt_required()
def studentDashboard():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student:
        return jsonify({"message": "Student not found"}), 404
    return jsonify(
        {"name": student.name, "branch": student.branch.value, "cgpa": student.cgpa}
    ), 200


@app.route("/api/admin", methods=["GET"])
@jwt_required()
def companyDashboard():
    current_user_id = get_jwt_identity()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")
