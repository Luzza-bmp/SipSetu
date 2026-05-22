from flask import Blueprint, request, jsonify
import os

from app.services.resume_parser import parse_resume

applicant_bp = Blueprint("applicant", __name__)

UPLOAD_FOLDER = "uploads"


@applicant_bp.route("/upload-resume", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(filepath)

    extracted_text = parse_resume(filepath)

    return jsonify({
        "message": "Resume parsed successfully",
        "filename": file.filename,
        "text": extracted_text
    })
