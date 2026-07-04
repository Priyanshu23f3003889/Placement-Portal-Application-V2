from datetime import datetime

from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


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
                "email": c.user.email,
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
            db.session.delete(drive)

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
                "studentId": a.student.id,
                "name": a.student.name,
                "driveId": a.driveId,
                "companyName": a.drive.company.name,
                "jobTitle": a.drive.jobTitle,
                "resumeUrl": a.resumeUrl,
                "applicationDate": a.applicationDate,
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
                "email": s.user.email,
                "resumeUrl": s.resumeUrl,
                "cgpa": s.cgpa,
                "isApproved": s.user.isActive,
                "branch": s.branch.value if hasattr(s.branch, "value") else s.branch,
            }
            for s in students
        ]
        return jsonify(students_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403


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


@app.route("/api/admin/Drives", methods=["GET"])
@jwt_required()
def adminDrives():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        drives = (
            db.session.execute(
                db.select(PlacementDrive).order_by(PlacementDrive.id.desc())
            )
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
            {"message": "Drive approval status updated", "status": drive.status}
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/admin/drives/<int:drive_id>/delete", methods=["DELETE"])
@jwt_required()
def toDrive(drive_id):
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
        for a in drive.applications:
            db.session.delete(a)
        db.session.delete(drive)

        db.session.commit()
        return jsonify({"message": "Drive Deleted", "status": drive.status}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route("/api/admin/placements", methods=["GET"])
@jwt_required()
def adminPlacement():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "ADMIN":
        placements = db.session.execute(db.select(Placement)).scalars().all()
        placements_data = [
            {
                "id": p.id,
                "studentName": p.studentName,
                "studentId": p.studentId,
                "driveId": p.driveId,
                "companyName": p.companyName,
                "position": p.position,
                "salary" : p.salary,
                "year" : p.year
            }
            for p in sorted(placements, key=lambda x : x.id, reverse = True)
        ]
        return jsonify(placements_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403
