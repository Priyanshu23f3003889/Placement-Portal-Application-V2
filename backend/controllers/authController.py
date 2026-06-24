from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
)
from werkzeug.security import check_password_hash, generate_password_hash


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
        name = data.get("name").strip()
        hrContact = data.get("hrContact").strip()
        website = data.get("website").strip()

        if len(hrContact) > 40 or len(hrContact)<6:
            return jsonify({"message": "Sorry, your HR Contact must be between 6 and 40 characters long."}), 400

        if not name or not hrContact or not website:
            return jsonify({"message": "Missing company details"}), 400

        msg = ""
        
        if db.session.scalar(db.select(Company).where(Company.name == name)):
            msg = "Company with this name already exists"
        elif db.session.scalar(db.select(Company).where(Company.hrContact == hrContact)):
            msg = "Company with this HR Contact already exists"
        elif db.session.scalar(db.select(Company).where(Company.website == website)):
            msg = "Company with this Website already exists"

        if msg :
            return jsonify({"message": msg}), 400

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
