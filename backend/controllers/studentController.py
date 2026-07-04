from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from datetime import datetime

@app.route("/api/student/profile", methods=["GET"])
@jwt_required()
def studentProfile():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404
    return jsonify(
        {
            "name": student.name,
            "branch": student.branch.value,
            "cgpa": student.cgpa,
            "email": student.user.email,
            "resumeUrl": student.resumeUrl,
            "id": student.id,
        }
    ), 200


@app.route("/api/student/profile/update", methods=["PATCH"])
@jwt_required()
def studentProfileUpadte():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    data = request.get_json()
    try:
        student.cgpa = data.get("cgpa")
        student.resumeUrl = data.get("resumeUrl")

        db.session.commit()
        return jsonify({"message": "Profile Updated"}), 200

    except:
        db.session.rollback()
        return jsonify({"message": "Profile Updation Failed"}), 403


@app.route("/api/student/companies", methods=["GET"])
@jwt_required()
def studentCompanies():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    if not student.user.isActive:
        return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 403

    companies = db.session.scalars(
        db.select(Company).where(Company.isApproved == True)
    ).all()

    comps = [
        {
            "name": c.name,
            "id": c.id,
            "website": c.website,
            "hrContact": c.hrContact,
            "email": c.user.email,
        }
        for c in companies
    ]

    return jsonify(comps), 200

@app.route("/api/student/drives", methods=["GET"])
@jwt_required()
def studentDrives():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    if not student.user.isActive:
        return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 403

    drives = db.session.scalars(
        db.select(PlacementDrive).where(PlacementDrive.status != DriveStatus.PENDING)
    ).all()

    drvs = [
        {
            "id": d.id,
            "jobTitle": d.jobTitle,
            "jobDescription": d.jobDescription,
            "deadline": d.deadline,
            "branch": d.branch,
            "cgpa": d.cgpa,
            "status": d.status,
            "isApplied" : any(a.studentId == student.id for a in d.applications),
            "companyName": d.company.name
        }
        for d in sorted(drives, key=lambda x : x.id, reverse=True)
    ]

    return jsonify(drvs), 200


@app.route("/api/student/drives/<int:id>/apply", methods=["POST"])
@jwt_required()
def studentDriveApply(id):
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    if not student.user.isActive:
        return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 403

    drive = db.session.scalar(
        db.select(PlacementDrive).where(PlacementDrive.id == id)
    )

    if drive.cgpa > student.cgpa:
        return jsonify({"message": "Application Failed : CGPA Criteria Not met"}), 403

    if drive.deadline < datetime.now() :
         return jsonify({"message": "Application Failed : Application Deadline is Over"}), 403

    try:
        if not any(a.driveId == id for a in student.applications):
            application = Application(studentId = student.id, driveId = id, resumeUrl = student.resumeUrl)
            db.session.add(application)
            db.session.commit()
            return jsonify({"message": "Applied"}), 200
        else:
            return jsonify({"message": "Already Applied to this Drive"}), 409

    except:
        db.session.rollback()
        return jsonify({"message": "Application Failed"}), 403



@app.route("/api/student/applications", methods=["GET"])
@jwt_required()
def studentApplications():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    if not student.user.isActive:
        return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 403

    apps = [
        {
            "id": a.id,
            "jobTitle": a.drive.jobTitle,
            "status": a.status,
            "resumeUrl" : a.resumeUrl,
            "driveId" : a.driveId,
            "companyName" : a.drive.company.name,
            "applicationDate" : a.applicationDate,
            "isApproved" : a.drive.company.isApproved
            
        }
        for a in sorted(student.applications, key=lambda x : x.applicationDate, reverse=True)
    ]

    return jsonify(apps), 200

@app.route("/api/student/placements", methods=["GET"])
@jwt_required()
def studentPlacements():
    current_user_id = get_jwt_identity()
    student = db.session.scalar(
        db.select(Student).where(Student.userId == int(current_user_id))
    )
    if not student or student.user.role.name != "STUDENT":
        return jsonify({"message": "Student not found"}), 404

    if not student.user.isActive:
        return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 403

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
               for p in sorted(student.placements, key=lambda x : x.id, reverse = True)
           ]

    return jsonify(placements_data), 200