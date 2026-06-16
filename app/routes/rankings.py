
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import text
 
from app import db
from app.models import Job, Recruiter, Ranking, Resume
from app.utils.embedder import embed_text
 
rankings_bp = Blueprint("rankings", __name__)
 
 
def _parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


@rankings_bp.route("/<job_id>/rank", methods=["GET"])
@jwt_required()
def rank_applicants(job_id):
    # ── 1. Auth guard: recruiters only ───────────────────────────────────────
    claims = get_jwt()
    if claims.get("role") != "recruiter":
        return jsonify({"error": "Only recruiters can access rankings"}), 403
 
    user_id   = get_jwt_identity()
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return jsonify({"error": "Invalid authenticated user id"}), 401

    recruiter = db.session.get(Recruiter, user_uuid)
    if not recruiter:
        return jsonify({"error": "Recruiter record not found"}), 404
 
    # ── 2. Validate job + ownership ──────────────────────────────────────────
    job_uuid = _parse_uuid(job_id)
    if job_uuid is None:
        return jsonify({"error": "Invalid job_id"}), 400

    job = db.session.get(Job, job_uuid)
    if not job:
        return jsonify({"error": "Job not found"}), 404
 
    if job.recruiter_id != user_uuid:
        return jsonify({"error": "You do not own this job"}), 403
 
    if not job.description:
        return jsonify({"error": "Job has no description; cannot compute semantic similarity"}), 422
 
    # ── 3. Scoring weights (overridable via query params) ────────────────────
    try:
        sem_w  = float(request.args.get("semantic_weight",   0.7))
        exp_w  = float(request.args.get("experience_weight", 0.3))
    except ValueError:
        return jsonify({"error": "Weights must be numeric"}), 400
 
    if abs(sem_w + exp_w - 1.0) > 0.01:
        return jsonify({"error": "semantic_weight + experience_weight must equal 1.0"}), 400
 
    required_years = float(job.required_experience_years or 0)
 
    # ── 4. Embed the job description (on the fly, not cached) ────────────────
    job_vector = embed_text(job.description)   # 384-dim list
    job_vector_str = "[" + ",".join(str(v) for v in job_vector) + "]"
 
    # ── 5. Database-level cosine ranking via pgvector ────────────────────────
    # Only resumes belonging to applicants who actually applied are included.
    # The <=> operator returns cosine DISTANCE (0 = identical, 2 = opposite),
    # so we compute similarity as  1 - distance.
    #
    # Experience score: 1 at exact match, decays linearly, floors at 0.
    sql = text("""
        SELECT
            r.resume_id,
            r.applicant_id,
            u.email,
            COALESCE(r.parsed_experience_years, 0)               AS experience_years,
            1 - (r.embedding <=> CAST(:job_vec AS vector))       AS semantic_score,
            GREATEST(
                0,
                1 - ABS(COALESCE(r.parsed_experience_years, 0) - :req_years) / 10.0
            )                                                     AS experience_score,
            -- weighted final score (computed in SQL for transparent ordering)
            :sem_w  * (1 - (r.embedding <=> CAST(:job_vec AS vector)))
          + :exp_w  * GREATEST(
                          0,
                          1 - ABS(COALESCE(r.parsed_experience_years, 0) - :req_years) / 10.0
                      )                                           AS final_score
        FROM public.resumes        r
        JOIN public.applications   a  ON a.applicant_id = r.applicant_id
        JOIN public.applicants     ap ON ap.user_id      = r.applicant_id
        JOIN public.users          u  ON u.user_id       = r.applicant_id
        WHERE a.job_id    = CAST(:job_id AS uuid)
          AND r.embedding IS NOT NULL
        -- Pick only the latest resume per applicant (subquery not needed; DISTINCT ON does it)
        ORDER BY r.applicant_id, r.uploaded_at DESC
    """)
 
    # Wrap in DISTINCT ON to keep only the newest resume per applicant,
    # then outer-sort by final_score.
    outer_sql = text("""
        WITH ranked AS (
            SELECT DISTINCT ON (r.applicant_id)
                r.resume_id,
                r.applicant_id,
                u.email,
                COALESCE(r.parsed_experience_years, 0)               AS experience_years,
                r.parsed_skills,
                1 - (r.embedding <=> CAST(:job_vec AS vector))       AS semantic_score,
                GREATEST(
                    0,
                    1 - ABS(COALESCE(r.parsed_experience_years, 0) - :req_years) / 10.0
                )                                                     AS experience_score,
                :sem_w  * (1 - (r.embedding <=> CAST(:job_vec AS vector)))
              + :exp_w  * GREATEST(
                              0,
                              1 - ABS(COALESCE(r.parsed_experience_years, 0) - :req_years) / 10.0
                          )                                           AS final_score
            FROM public.resumes        r
            JOIN public.applications   a  ON a.applicant_id = r.applicant_id
            JOIN public.users          u  ON u.user_id       = r.applicant_id
            WHERE a.job_id    = CAST(:job_id AS uuid)
              AND r.embedding IS NOT NULL
            ORDER BY r.applicant_id, r.uploaded_at DESC
        )
        SELECT *, ROW_NUMBER() OVER (ORDER BY final_score DESC) AS candidate_rank
        FROM ranked
        ORDER BY final_score DESC
    """)
 
    rows = db.session.execute(
        outer_sql,
        {
            "job_vec":   job_vector_str,
            "job_id":    str(job_uuid),
            "req_years": required_years,
            "sem_w":     sem_w,
            "exp_w":     exp_w,
        },
    ).fetchall()
 
    if not rows:
        return jsonify({"message": "No applicants with processed resumes found for this job", "rankings": []}), 200
 
    # ── 6. Persist rankings to DB (upsert pattern) ───────────────────────────
    # Delete stale rankings for this job, then bulk-insert fresh ones.
    Ranking.query.filter_by(job_id=job_uuid).delete()
 
    ranking_objects = []
    results = []
    for row in rows:
        rk = Ranking(
            job_id           = job_uuid,
            resume_id        = row.resume_id,
            semantic_score   = float(row.semantic_score),
            experience_score = float(row.experience_score),
            matching_score   = float(row.final_score),
            candidate_rank   = int(row.candidate_rank),
            status           = "Pending",
        )
        ranking_objects.append(rk)
        results.append({
            "rank":              int(row.candidate_rank),
            "applicant_email":   row.email,
            "applicant_id":      str(row.applicant_id),
            "resume_id":         str(row.resume_id),
            "semantic_score":    round(float(row.semantic_score), 4),
            "experience_score":  round(float(row.experience_score), 4),
            "final_score":       round(float(row.final_score), 4),
            "experience_years":  float(row.experience_years),
            "skills":            row.parsed_skills.split("|") if row.parsed_skills else [],
            "status":            "Pending",
        })
 
    db.session.bulk_save_objects(ranking_objects)
    db.session.commit()
 
    return jsonify({
        "job_id":    str(job_uuid),
        "job_title": job.title,
        "weights":   {"semantic": sem_w, "experience": exp_w},
        "total":     len(results),
        "rankings":  results,
    }), 200
 
 
# ── Update application status (recruiter shortlists / rejects) ──────────────
 
@rankings_bp.route("/<job_id>/rank/<resume_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(job_id, resume_id):
    """PATCH body: {"status": "Shortlisted"} or {"status": "Rejected"}"""
    claims = get_jwt()
    if claims.get("role") != "recruiter":
        return jsonify({"error": "Only recruiters can update status"}), 403
 
    user_id = get_jwt_identity()
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return jsonify({"error": "Invalid authenticated user id"}), 401

    recruiter = db.session.get(Recruiter, user_uuid)
    if not recruiter:
        return jsonify({"error": "Recruiter record not found"}), 404

    job_uuid = _parse_uuid(job_id)
    resume_uuid = _parse_uuid(resume_id)
    if job_uuid is None:
        return jsonify({"error": "Invalid job_id"}), 400
    if resume_uuid is None:
        return jsonify({"error": "Invalid resume_id"}), 400

    job = db.session.get(Job, job_uuid)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job.recruiter_id != user_uuid:
        return jsonify({"error": "You do not own this job"}), 403

    data      = request.get_json(silent=True) or {}
    new_status = str(data.get("status") or "").strip()
    if new_status not in ("Pending", "Shortlisted", "Rejected"):
        return jsonify({"error": "status must be Pending, Shortlisted, or Rejected"}), 400
 
    ranking = Ranking.query.filter_by(
        job_id=job_uuid,
        resume_id=resume_uuid,
    ).first()
    if not ranking:
        return jsonify({"error": "Ranking record not found; run /rank first"}), 404
 
    ranking.status = new_status
    db.session.commit()
 
    return jsonify({"message": f"Status updated to {new_status}"}), 200
