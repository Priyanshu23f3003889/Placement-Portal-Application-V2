from database.models import *
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


@app.route("/api/admin", methods=["GET"])
@jwt_required()
def companyDashboard():
    current_user_id = get_jwt_identity()
    # The original function in controller.py was incomplete.
    return jsonify({"message": "Company dashboard placeholder"}), 200
