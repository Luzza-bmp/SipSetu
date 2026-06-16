import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename

from app import db
from app.models import Applicant, Resume, Skill, resume_skills
from app.utils.resume_parser import parse_resume
from app.utils.embedder import embed_text

resumes_bp = Blueprint("resumes", __name__)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


def _parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _extract_text(file_path: str, filename: str) -> str:
    """Extract raw text from uploaded file."""
    ext = filename.rsplit(".", 1)[1].lower()

    if ext == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            # Fallback: PyPDF2 (lighter)
            import PyPDF2
            text = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)

    if ext == "docx":
        import docx
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""


@resumes_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    # ── 1. Auth guard: applicants only ───────────────────────────────────────
    claims = get_jwt()
    if claims.get("role") != "applicant":
        return jsonify({"error": "Only applicants can upload resumes"}), 403

    user_id = get_jwt_identity()
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return jsonify({"error": "Invalid authenticated user id"}), 401

    applicant = db.session.get(Applicant, user_uuid)
    if not applicant:
        return jsonify({"error": "Applicant record not found"}), 404

    # ── 2. File validation ────────────────────────────────────────────────────
    if "resume" not in request.files:
        return jsonify({"error": "No file field named 'resume' in request"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    # ── 3. Save file to disk ──────────────────────────────────────────────────
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(file_path)

    # ── 4. Extract text ───────────────────────────────────────────────────────
    raw_text = _extract_text(file_path, file.filename)
    if not raw_text.strip():
        os.remove(file_path)
        return jsonify({"error": "Could not extract text from file. Is it a scanned image PDF?"}), 422

    # ── 5. Parse resume sections (anti-gaming: only Skills + Experience fed to embedder)
    parsed = parse_resume(raw_text)

    # ── 6. Generate embedding ─────────────────────────────────────────────────
    embedding = embed_text(parsed["embedding_input"])   # 384-dim list

    # ── 7. Upsert skills into the skills table ────────────────────────────────
    skill_objects = []
    for skill_name in parsed["skills_list"]:
        skill_name_clean = skill_name.strip().lower()
        if not skill_name_clean:
            continue
        existing = Skill.query.filter_by(skill_name=skill_name_clean).first()
        if not existing:
            existing = Skill(skill_name=skill_name_clean)
            db.session.add(existing)
            db.session.flush()   # get skill_id before commit
        skill_objects.append(existing)

    # ── 8. Persist Resume ─────────────────────────────────────────────────────
    new_resume = Resume(
        applicant_id            = user_uuid,
        raw_text                = raw_text,
        file_path               = file_path,
        embedding               = embedding,
        parsed_skills           = "|".join(parsed["skills_list"]),
        parsed_experience_years = parsed["experience_years"],
    )
    new_resume.skills = skill_objects
    db.session.add(new_resume)
    db.session.commit()

    return jsonify({
        "message":            "Resume uploaded and processed successfully",
        "resume_id":          str(new_resume.resume_id),
        "skills_extracted":   parsed["skills_list"],
        "experience_years":   float(parsed["experience_years"] or 0),
        "embedding_dims":     len(embedding),
    }), 201
