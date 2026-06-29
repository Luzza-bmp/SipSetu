from flask import Blueprint, request, jsonify
import os
from app import db
from app.models import Applicant, Resume, Skill, Ranking, Job
from app.services.resume_parser import parse_resume
from app.services.pdf_parser import extract_pdf_text
from app.services.docx_parser import extract_docx_text
from app.utils.matcher import match_skills
from app.utils.scorer import calculate_score
from app.utils.feedback import generate_feedback
from app.utils.extractor import extract_skills

applicant_bp = Blueprint("applicant", __name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_rankings_for_resume(resume_id, applicant_id):
    resume = Resume.query.get(resume_id)
    if not resume:
        return
        
    all_jobs = Job.query.all()
    resume_skills = [s.skill_name for s in resume.skills]
    
    for job in all_jobs:
        job_skills = [s.skill_name for s in job.skills]
        matched, missing = match_skills(resume_skills, job_skills)
        score = calculate_score(matched, job_skills)
        
        existing_ranking = Ranking.query.filter_by(job_id=job.job_id, resume_id=resume_id).first()
        if existing_ranking:
            existing_ranking.matching_score = score
        else:
            ranking = Ranking(
                job_id=job.job_id,
                resume_id=resume_id,
                matching_score=score,
                status='Pending'
            )
            db.session.add(ranking)
            
    db.session.commit()

# ============ RESUME UPLOAD ROUTE ============

@applicant_bp.route("/upload-resume", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    applicant_id = request.form.get("applicant_id") or request.args.get("applicant_id")

    if not applicant_id:
        return jsonify({"error": "Missing applicant_id"}), 400

    # Verify applicant exists
    applicant = Applicant.query.get(applicant_id)
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1. Parse resume to get structured data (e.g. skills)
    parsed_data = parse_resume(filepath)
    if "error" in parsed_data:
        return jsonify({"error": parsed_data["error"]}), 400

    # 2. Extract full raw text
    try:
        if filepath.endswith(".pdf"):
            raw_text = extract_pdf_text(filepath)
        elif filepath.endswith(".docx"):
            raw_text = extract_docx_text(filepath)
        else:
            raw_text = ""
    except Exception as e:
        raw_text = "Text extraction error: " + str(e)

    # 3. Save resume to db
    new_resume = Resume(
        applicant_id=applicant_id,
        raw_text=raw_text,
        file_path=filepath
    )
    db.session.add(new_resume)
    db.session.flush()  # Get resume_id

    # 4. Save resume skills
    skills_extracted = parsed_data.get("skills", [])
    for skill_name in skills_extracted:
        if not skill_name.strip():
            continue
        skill = Skill.query.filter_by(skill_name=skill_name.lower()).first()
        if not skill:
            skill = Skill(skill_name=skill_name.lower())
            db.session.add(skill)
        if skill not in new_resume.skills:
            new_resume.skills.append(skill)

    db.session.commit()

    # 5. Create rankings against all existing jobs
    create_rankings_for_resume(new_resume.resume_id, applicant_id)

    return jsonify({
        "message": "Resume uploaded and parsed successfully",
        "resume_id": str(new_resume.resume_id),
        "filename": file.filename,
        "skills_extracted": skills_extracted,
        "parsed_data": parsed_data
    }), 201

# ============ RESUMES LIST ROUTE ============

@applicant_bp.route("/resumes", methods=["GET"])
def get_resumes():
    applicant_id = request.args.get("applicant_id")
    if not applicant_id:
        return jsonify({"error": "Missing applicant_id"}), 400

    # Verify applicant exists
    applicant = Applicant.query.get(applicant_id)
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404

    resumes_list = Resume.query.filter_by(applicant_id=applicant_id).all()
    
    result = [{
        "resume_id": str(r.resume_id),
        "uploaded_at": r.uploaded_at.isoformat(),
        "file_path": r.file_path,
        "skills": [s.skill_name for s in r.skills]
    } for r in resumes_list]

    return jsonify(result), 200

# ============ JOB MATCHES ROUTES ============

def fetch_matched_jobs(applicant_id, page, per_page, min_score):
    applicant = Applicant.query.get(applicant_id)
    if not applicant:
        return None, "Applicant not found"
        
    latest_resume = Resume.query.filter_by(applicant_id=applicant_id).order_by(Resume.uploaded_at.desc()).first()
    if not latest_resume:
        return None, "No resume found for applicant"
        
    query = Ranking.query.filter(
        Ranking.resume_id == latest_resume.resume_id,
        Ranking.matching_score >= min_score
    ).order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    matched_jobs_list = []
    resume_skills = [s.skill_name for s in latest_resume.skills]
    
    for r in rankings:
        job_skills = [s.skill_name for s in r.job.skills]
        matched, missing = match_skills(resume_skills, job_skills)
        feedback = generate_feedback(r.matching_score, missing)
        
        matched_jobs_list.append({
            "job_id": str(r.job.job_id),
            "title": r.job.title,
            "recruiter_name": r.job.recruiter.name if r.job.recruiter.name else r.job.recruiter.email,
            "recruiter_company": r.job.recruiter.company,
            "matching_score": r.matching_score,
            "status": r.status,
            "matched_skills": matched,
            "missing_skills": missing,
            "feedback": feedback
        })
        
    result = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "resume_id": str(latest_resume.resume_id),
        "matched_jobs": matched_jobs_list
    }
    return result, None

@applicant_bp.route("/matched-jobs", methods=["GET"])
def get_matched_jobs_query():
    applicant_id = request.args.get("applicant_id")
    if not applicant_id:
        return jsonify({"error": "Missing applicant_id"}), 400
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    
    result, error = fetch_matched_jobs(applicant_id, page, per_page, min_score)
    if error:
        status_code = 404 if "not found" in error or "No resume" in error else 400
        return jsonify({"error": error}), status_code
        
    return jsonify(result), 200

@applicant_bp.route("/applicants/<applicant_id>/matched-jobs", methods=["GET"])
def get_matched_jobs_path(applicant_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    
    result, error = fetch_matched_jobs(applicant_id, page, per_page, min_score)
    if error:
        status_code = 404 if "not found" in error or "No resume" in error else 400
        return jsonify({"error": error}), status_code
        
    return jsonify(result), 200

@applicant_bp.route("/analyze-job", methods=["POST"])
def analyze_job():
    data = request.get_json() or {}
    description = data.get("description", "")
    if not description:
        return jsonify({"error": "Missing description"}), 400
    skills = extract_skills(description)
    return jsonify({"skills": skills}), 200

@applicant_bp.route("/match", methods=["POST"])
def match_candidate_job():
    data = request.get_json() or {}
    candidate_id = data.get("candidate_id")
    job_id = data.get("job_id")
    
    if not candidate_id or not job_id:
        return jsonify({"error": "Missing candidate_id or job_id"}), 400
        
    applicant = Applicant.query.get(candidate_id)
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404
        
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    latest_resume = Resume.query.filter_by(applicant_id=candidate_id).order_by(Resume.uploaded_at.desc()).first()
    if not latest_resume:
        return jsonify({"error": "No resume found for applicant"}), 404
        
    resume_skills = [s.skill_name for s in latest_resume.skills]
    job_skills = [s.skill_name for s in job.skills]
    
    matched, missing = match_skills(resume_skills, job_skills)
    score = calculate_score(matched, job_skills)
    
    # Send score data to recruiter side (update/create ranking)
    existing_ranking = Ranking.query.filter_by(job_id=job_id, resume_id=latest_resume.resume_id).first()
    if existing_ranking:
        existing_ranking.matching_score = score
    else:
        ranking = Ranking(
            job_id=job_id,
            resume_id=latest_resume.resume_id,
            matching_score=score,
            status='Pending'
        )
        db.session.add(ranking)
        
    db.session.commit()
    
    return jsonify({
        "candidate_id": str(candidate_id),
        "job_id": str(job_id),
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }), 200

