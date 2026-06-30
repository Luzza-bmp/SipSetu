from flask import Blueprint, request, jsonify
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.resume_parser import parse_resume
from app.repositories.applicant_repository import save_applicant

applicant_bp = Blueprint("applicant", __name__)

UPLOAD_FOLDER = "uploads"


@applicant_bp.route("/upload-resume", methods=["POST"])
@jwt_required()
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(filepath)

    parsed_resume = parse_resume(filepath)
    user_id = get_jwt_identity()
    applicant_id = save_applicant(user_id, parsed_resume)

    return jsonify({

        "message": "Resume uploaded successfully",

        "applicant_id": applicant_id,

        "data": parsed_resume

    })
