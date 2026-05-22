from datetime import datetime

from database.models import *
from flask import current_app as app
from flask import jsonify, redirect, render_template, request, session, url_for
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.util.langhelpers import methods_equivalent
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


@app.route("/api/admin", methods=["GET"])
@jwt_required()
def adminDashboard():
    current_user_id = get_jwt_identity()
    print(current_user_id)


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
