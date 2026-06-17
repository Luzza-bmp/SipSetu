from flask import Blueprint, request, jsonify
from app import db
from app.models import Recruiter, Job, Skill, Ranking, Resume
from app.utils.extractor import extract_skills
from app.utils.matcher import match_skills
from app.utils.scorer import calculate_score
from app.utils.feedback import generate_feedback

recruiter_bp = Blueprint("recruiter", __name__)

def create_rankings_for_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return
        
    all_resumes = Resume.query.all()
    job_skills = [s.skill_name for s in job.skills]
    
    for resume in all_resumes:
        resume_skills = [s.skill_name for s in resume.skills]
        matched, missing = match_skills(resume_skills, job_skills)
        score = calculate_score(matched, job_skills)
        
        existing_ranking = Ranking.query.filter_by(job_id=job_id, resume_id=resume.resume_id).first()
        if existing_ranking:
            existing_ranking.matching_score = score
        else:
            ranking = Ranking(
                job_id=job_id,
                resume_id=resume.resume_id,
                matching_score=score,
                status='Pending'
            )
            db.session.add(ranking)
            
    db.session.commit()

# ============ JOB POSTING ROUTES ============

@recruiter_bp.route('/jobs', methods=['GET', 'POST'])
def jobs():
    """List all jobs or create a new job posting"""
    if request.method == 'POST':
        data = request.get_json()
        recruiter_id = data.get('recruiter_id')
        title = data.get('title')
        description = data.get('description', '')
        skills_input = data.get('skills', [])
        
        if not recruiter_id or not title:
            return jsonify({"error": "Missing recruiter_id or title"}), 400
        
        # Verify recruiter exists
        recruiter = Recruiter.query.get(recruiter_id)
        if not recruiter:
            return jsonify({"error": "Recruiter not found"}), 404
            
        new_job = Job(recruiter_id=recruiter_id, title=title)
        
        # Combine provided skills with skills extracted from description
        skills_set = set()
        for s in skills_input:
            if s.strip():
                skills_set.add(s.strip().lower())
                
        if description:
            extracted = extract_skills(description)
            for s in extracted:
                skills_set.add(s.lower())
        
        for skill_name in skills_set:
            skill = Skill.query.filter_by(skill_name=skill_name).first()
            if not skill:
                skill = Skill(skill_name=skill_name)
                db.session.add(skill)
            if skill not in new_job.skills:
                new_job.skills.append(skill)
            
        db.session.add(new_job)
        db.session.commit()
        
        # Update rankings for this new job against all resumes
        create_rankings_for_job(new_job.job_id)
        
        return jsonify({
            "message": "Job posted successfully",
            "job_id": str(new_job.job_id),
            "title": new_job.title,
            "skills": [s.skill_name for s in new_job.skills]
        }), 201
        
    elif request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Job.query.paginate(page=page, per_page=per_page, error_out=False)
        jobs_list = pagination.items
        
        result = {
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
            "jobs": [{
                "job_id": str(job.job_id),
                "title": job.title,
                "recruiter_id": str(job.recruiter_id),
                "recruiter_name": job.recruiter.name if job.recruiter.name else job.recruiter.email,
                "created_at": job.created_at.isoformat(),
                "skills": [s.skill_name for s in job.skills]
            } for job in jobs_list]
        }
        
        return jsonify(result), 200

@recruiter_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get details of a specific job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    result = {
        "job_id": str(job.job_id),
        "title": job.title,
        "recruiter_id": str(job.recruiter_id),
        "recruiter_name": job.recruiter.name if job.recruiter.name else job.recruiter.email,
        "recruiter_company": job.recruiter.company,
        "created_at": job.created_at.isoformat(),
        "skills": [s.skill_name for s in job.skills]
    }
    
    return jsonify(result), 200

# ============ CANDIDATE MATCHING & RANKING ROUTES ============

@recruiter_bp.route('/jobs/<job_id>/candidates', methods=['GET'])
def get_job_candidates(job_id):
    """Get all candidates for a specific job, ranked by match score"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    status_filter = request.args.get('status')
    
    query = Ranking.query.filter(
        Ranking.job_id == job_id,
        Ranking.matching_score >= min_score
    )
    
    if status_filter:
        query = query.filter(Ranking.status == status_filter)
        
    query = query.order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    candidates_list = []
    job_skills = [s.skill_name for s in job.skills]
    
    for idx, r in enumerate(rankings):
        resume_skills = [s.skill_name for s in r.resume.skills]
        matched, missing = match_skills(resume_skills, job_skills)
        feedback = generate_feedback(r.matching_score, missing)
        
        # Calculate rank dynamically within the query result context
        cand_rank = (page - 1) * per_page + idx + 1
        
        candidates_list.append({
            "ranking_id": str(r.ranking_id),
            "applicant_id": str(r.resume.applicant_id),
            "applicant_name": r.resume.applicant.name if r.resume.applicant.name else r.resume.applicant.email,
            "applicant_email": r.resume.applicant.email,
            "applicant_location": r.resume.applicant.location,
            "matching_score": r.matching_score,
            "candidate_rank": r.candidate_rank or cand_rank,
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
        "job_id": str(job_id),
        "job_title": job.title,
        "candidates": candidates_list
    }
    
    return jsonify(result), 200

@recruiter_bp.route('/candidates', methods=['GET'])
def get_recruiter_candidates():
    """Get all candidates for all jobs posted by a recruiter"""
    recruiter_id = request.args.get('recruiter_id')
    if not recruiter_id:
        return jsonify({"error": "Missing recruiter_id"}), 400
        
    recruiter = Recruiter.query.get(recruiter_id)
    if not recruiter:
        return jsonify({"error": "Recruiter not found"}), 404
        
    recruiter_jobs = Job.query.filter_by(recruiter_id=recruiter_id).all()
    job_ids = [job.job_id for job in recruiter_jobs]
    
    if not job_ids:
        return jsonify({
            "total": 0,
            "recruiter_id": str(recruiter_id),
            "candidates": []
        }), 200
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    status_filter = request.args.get('status')
    
    query = Ranking.query.filter(
        Ranking.job_id.in_(job_ids),
        Ranking.matching_score >= min_score
    )
    
    if status_filter:
        query = query.filter(Ranking.status == status_filter)
        
    query = query.order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    candidates_list = []
    for r in rankings:
        job_skills = [s.skill_name for s in r.job.skills]
        resume_skills = [s.skill_name for s in r.resume.skills]
        matched, missing = match_skills(resume_skills, job_skills)
        
        candidates_list.append({
            "ranking_id": str(r.ranking_id),
            "job_id": str(r.job.job_id),
            "job_title": r.job.title,
            "applicant_id": str(r.resume.applicant_id),
            "applicant_name": r.resume.applicant.name if r.resume.applicant.name else r.resume.applicant.email,
            "applicant_email": r.resume.applicant.email,
            "matching_score": r.matching_score,
            "status": r.status,
            "matched_skills": matched,
            "missing_skills": missing
        })
        
    result = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "recruiter_id": str(recruiter_id),
        "candidates": candidates_list
    }
    
    return jsonify(result), 200

@recruiter_bp.route('/rankings/<ranking_id>', methods=['PUT'])
def update_ranking(ranking_id):
    """Update candidate ranking/status or candidate_rank"""
    ranking = Ranking.query.get(ranking_id)
    if not ranking:
        return jsonify({"error": "Ranking not found"}), 404
    
    data = request.get_json()
    
    if 'candidate_rank' in data:
        ranking.candidate_rank = data.get('candidate_rank')
        
    if 'status' in data:
        status_val = data.get('status')
        if status_val not in ['Pending', 'Shortlisted', 'Rejected']:
            return jsonify({"error": "Invalid status. Must be Pending, Shortlisted, or Rejected"}), 400
        ranking.status = status_val
        
    db.session.commit()
    
    return jsonify({
        "message": "Ranking updated successfully",
        "ranking_id": str(ranking.ranking_id),
        "candidate_rank": ranking.candidate_rank,
        "status": ranking.status
    }), 200
