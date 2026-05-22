from flask import Blueprint, request, jsonify
import os

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

    return jsonify({
        "message": "Resume uploaded successfully",
        "filename": file.filename
    })
