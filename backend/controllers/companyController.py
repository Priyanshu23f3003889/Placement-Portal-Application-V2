from datetime import datetime

from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from flask_jwt_extended.utils import current_user


@app.route("/api/company/profile", methods=["GET"])
@jwt_required()
def companyProfile():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))
        return jsonify(
            {
                "id": company.id,
                "name": company.name,
                "email": user.email,
                "hrContact": company.hrContact,
                "website": company.website,
                "isApproved": company.isApproved,
            }
        ), 200
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/profile/update", methods=["PATCH"])
@jwt_required()
def updateCompanyProfile():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))
        if not company:
            return jsonify({"message": "Company profile not found"}), 404

        data = request.get_json()
        website = (data.get("website") or "").strip()
        hrContact = (data.get("hrContact") or "").strip()

        if not website or not hrContact:
            return jsonify({"message": "Website and HR Contact are required"}), 400

        print(hrContact, len(hrContact))
        if len(hrContact) > 40 or len(hrContact)<6:
            return jsonify({"message": "Sorry, your HR Contact must be between 6 and 40 characters long."}), 400
        
        comp = db.session.scalar(
            db.select(Company).where(
                Company.hrContact == hrContact, Company.id != company.id
            )
        )
        if comp:
            return jsonify(
                {"message": "Company with this HR Contact already exists"}
            ), 409

        comp = db.session.scalar(
            db.select(Company).where(
                Company.website == website, Company.id != company.id
            )
        )
        if comp:
            return jsonify({"message": "Company with this Website already exists"}), 409

        company.website = website
        company.hrContact = hrContact
        db.session.commit()
        return jsonify({"message": "Updated"}), 200
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/drives", methods=["GET"])
@jwt_required()
def companyDrives():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))
        if not company.isApproved:
            return jsonify({"message": "Blacklisted/Pending Approval By ADMIN"}), 403
        drives = [
            {
                "id": d.id,
                "jobTitle": d.jobTitle,
                "jobDescription": d.jobDescription,
                "deadline": d.deadline,
                "branch": d.branch,
                "cgpa": d.cgpa,
                "status": d.status,
            }
            for d in sorted(company.drives, key=lambda x : x.id, reverse=True)
        ]
        if drives:
            return jsonify(drives), 200
        else:
            return jsonify({"message": "No drives Found"}), 403
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/drives/<int:drive_id>/close", methods=["PATCH"])
@jwt_required()
def closeDrive(drive_id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))
        drive = db.session.scalar(
            db.select(PlacementDrive).where(
                PlacementDrive.id == drive_id, PlacementDrive.companyId == company.id
            )
        )

        if not drive:
            return jsonify({"message": "Drive not found or access denied"}), 404

        drive.status = DriveStatus.CLOSED

        for application in drive.applications:
            if application.status in [
                ApplicationStatus.APPLIED,
                ApplicationStatus.SHORTLISTED,
            ]:
                application.status = ApplicationStatus.REJECTED

        db.session.commit()
        return jsonify({"message": "Drive closed successfully"}), 200
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/createdrive", methods=["POST"])
@jwt_required()
def createDrive():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))

        if not company.isApproved:
            return jsonify({"message": "Blacklisted / Pending Approval by ADMIN"}), 403

        data = request.get_json()
        deadline = datetime.fromisoformat(data.get("deadline"))
        jobTitle = data.get("jobTitle")
        jobDescription = data.get("jobDescription")
        branch = data.get("branch")
        cgpa = data.get("cgpa")

        newDrive = PlacementDrive(
            companyId=company.id,
            jobTitle=jobTitle,
            jobDescription=jobDescription,
            branch=branch,
            deadline=deadline,
            cgpa=cgpa,
            year=datetime.now().year,
            status=DriveStatus.APPROVED
        )
        db.session.add(newDrive)
        db.session.commit()
        return jsonify({"message": "Drive Created"}), 200
    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/editdrive/<int:id>", methods=["GET", "POST"])
@jwt_required()
def editDrive(id):
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))
    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id))
        drive = db.session.scalar(
            db.select(PlacementDrive).where(
                PlacementDrive.id == id, PlacementDrive.companyId == company.id
            )
        )

        if not drive or not company.isApproved:
            return jsonify({"message": "Drive not found or access denied"}), 404
        if request.method == "GET":
            driveDetails = {
                    "id": drive.id,
                    "jobTitle": drive.jobTitle,
                    "jobDescription": drive.jobDescription,
                    "deadline": drive.deadline.isoformat(timespec='seconds'),
                    "branch": drive.branch.name,
                    "cgpa": drive.cgpa,
                    "status": drive.status,
                    "companyId" : drive.companyId
                }
            return jsonify(driveDetails), 200
        else:
            data = request.get_json()
            
            drive.deadline = datetime.fromisoformat(data.get("deadline"))
            drive.jobTitle = data.get("jobTitle")
            drive.jobDescription = data.get("jobDescription")
            drive.branch = data.get("branch")
            drive.cgpa = data.get("cgpa")

            db.session.commit()
            return jsonify({"message": "Drive Edited"}), 200
    else:
        db.session.rollback()
        return jsonify({"message": "Access Denied"}), 403

@app.route("/api/company/applications", methods=["GET"])
@jwt_required()
def companyApplications():
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id)) 
        if not company.isApproved:
            return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 404
        applications = []
        for d in company.drives:
            for a in d.applications:
                applications.append(a)
                
        apps_data = [
            {
                "id": a.id,
                "studentId": a.student.id,
                "name": a.student.name,
                "driveId": a.driveId,
                "companyName": a.drive.company.name,
                "jobTitle": a.drive.jobTitle,
                "resumeUrl": a.student.resumeUrl,
                "applicationDate": a.applicationDate,
                "status": a.status.value if hasattr(a.status, "value") else a.status,
            }
            for a in sorted(applications, key = lambda x : x.driveId, reverse = True)
        ]
        return jsonify(apps_data), 200

    else:
        return jsonify({"message": "Access Denied"}), 403


@app.route("/api/company/applications/changestatus/<int:appId>/<int:rejected>", methods = ["PATCH"])
@jwt_required()
def changeStatus(appId, rejected) :
    current_user_id = get_jwt_identity()
    user = db.session.scalar(db.select(User).where(User.id == int(current_user_id)))

    if user.role.name == "COMPANY":
        company = db.session.scalar(db.select(Company).where(Company.userId == user.id)) 
        if not company.isApproved:
            return jsonify({"message": "Blacklisted/Pending Approval from ADMIN"}), 404

        application = db.session.scalar(db.select(Application).where(Application.id == appId))

        if not application:
            return jsonify({"message": "Application does not Exist"}), 404

        if application.drive.companyId != company.id :
            return jsonify({"message": "This Application does not belong to any of your Drives"}), 404

        try:
            if rejected:
                application.status = ApplicationStatus.REJECTED
                
            elif application.status == ApplicationStatus.APPLIED or application.status == ApplicationStatus.REJECTED:
                application.status = ApplicationStatus.SHORTLISTED

            else:
                application.status = ApplicationStatus.SELECTED
            

            db.session.commit()
            return jsonify({"message": "Application status changed"}), 200
                
                
        except:
            db.session.rollback()

            return jsonify({"message": "Failed to change the Application status"}), 404
            

    else:
        return jsonify({"message": "Access Denied"}), 403
