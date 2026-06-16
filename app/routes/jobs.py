
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
 
from app import db
from app.models import Job, Recruiter, Applicant, Resume, Application, Skill
 
jobs_bp = Blueprint("jobs", __name__)


def _parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None
 
 
# ── Create a job (recruiter only) ────────────────────────────────────────────
 
@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def create_job():
    claims = get_jwt()
    if claims.get("role") != "recruiter":
        return jsonify({"error": "Only recruiters can create jobs"}), 403
 
    user_id   = get_jwt_identity()
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return jsonify({"error": "Invalid authenticated user id"}), 401

    recruiter = db.session.get(Recruiter, user_uuid)
    if not recruiter:
        return jsonify({"error": "Recruiter record not found"}), 404
 
    data = request.get_json(silent=True) or {}
    title                    = str(data.get("title") or "").strip()
    description              = str(data.get("description") or "").strip()
    try:
        required_experience_years = float(data.get("required_experience_years", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "required_experience_years must be numeric"}), 400
    skill_names              = data.get("skills", [])   # list of strings
 
    if not title:
        return jsonify({"error": "title is required"}), 400
    if not description:
        return jsonify({"error": "description is required — it is used for semantic ranking"}), 400
 
    if not isinstance(skill_names, list):
        return jsonify({"error": "skills must be a list of strings"}), 400

    # Upsert skills
    skill_objects = []
    for sn in skill_names:
        if not isinstance(sn, str):
            return jsonify({"error": "skills must be a list of strings"}), 400
        sn_clean = sn.strip().lower()
        if not sn_clean:
            continue
        skill = Skill.query.filter_by(skill_name=sn_clean).first()
        if not skill:
            skill = Skill(skill_name=sn_clean)
            db.session.add(skill)
            db.session.flush()
        skill_objects.append(skill)
 
    job = Job(
        recruiter_id              = user_uuid,
        title                     = title,
        description               = description,
        required_experience_years = required_experience_years,
    )
    job.skills = skill_objects
    db.session.add(job)
    db.session.commit()
 
    return jsonify({
        "message":  "Job created",
        "job_id":   str(job.job_id),
        "title":    job.title,
    }), 201
 
 
# ── Apply to a job (applicant only) ──────────────────────────────────────────
 
@jobs_bp.route("/<job_id>/apply", methods=["POST"])
@jwt_required()
def apply_to_job(job_id):
    claims = get_jwt()
    if claims.get("role") != "applicant":
        return jsonify({"error": "Only applicants can apply to jobs"}), 403
 
    user_id   = get_jwt_identity()
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return jsonify({"error": "Invalid authenticated user id"}), 401

    applicant = db.session.get(Applicant, user_uuid)
    if not applicant:
        return jsonify({"error": "Applicant record not found"}), 404
 
    job_uuid = _parse_uuid(job_id)
    if job_uuid is None:
        return jsonify({"error": "Invalid job_id"}), 400

    job = db.session.get(Job, job_uuid)
    if not job:
        return jsonify({"error": "Job not found"}), 404
 
    # Check applicant has at least one resume with an embedding
    resume = (
        Resume.query
        .filter_by(applicant_id=user_uuid)
        .filter(Resume.embedding.isnot(None))
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        return jsonify({"error": "Please upload a resume before applying"}), 422
 
    # Prevent duplicate applications
    existing = Application.query.filter_by(
        job_id=job_uuid,
        applicant_id=user_uuid,
    ).first()
    if existing:
        return jsonify({"message": "Already applied", "application_id": str(existing.application_id)}), 200
 
    application = Application(
        job_id       = job_uuid,
        applicant_id = user_uuid,
    )
    db.session.add(application)
    db.session.commit()
 
    return jsonify({
        "message":        "Application submitted",
        "application_id": str(application.application_id),
        "job_id":         job_id,
    }), 201
 
 
# ── List jobs (any authenticated user) ───────────────────────────────────────
 
@jobs_bp.route("/", methods=["GET"])
@jwt_required()
def list_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return jsonify([
        {
            "job_id":                    str(j.job_id),
            "title":                     j.title,
            "required_experience_years": float(j.required_experience_years or 0),
            "created_at":                j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]), 200
