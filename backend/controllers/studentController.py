from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


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
