from flask import Blueprint, request, jsonify
from models import db, User, Applicant, Recruiter, Job, Resume, Skill, Ranking
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import func

api = Blueprint('api', __name__)

# ============ UTILITY FUNCTIONS ============

def extract_skills_from_text(text):
    """
    Extract skills from resume text using simple keyword matching.
    Returns a list of skill names found in the text.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    common_skills = [
        'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
        'react', 'angular', 'vue', 'svelte', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'graphql', 'rest api',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
        'html', 'css', 'tailwind', 'bootstrap', 'sass', 'webpack', 'vite', 'webpack',
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
        'design', 'figma', 'ui', 'ux', 'product', 'agile', 'scrum', 'jira',
        'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking'
    ]
    
    found_skills = []
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills

def calculate_match_score(resume_skills_list, job_skills_list):
    """
    Calculate similarity score between resume skills and job skills using TF-IDF.
    Returns a score between 0 and 100.
    """
    if not job_skills_list:
        return 0.0
    
    if not resume_skills_list:
        return 0.0
    
    # Create a simple TF-IDF based score
    resume_set = set([s.lower() for s in resume_skills_list])
    job_set = set([s.lower() for s in job_skills_list])
    
    if len(job_set) == 0:
        return 0.0
    
    # Jaccard similarity
    intersection = len(resume_set.intersection(job_set))
    union = len(resume_set.union(job_set))
    
    if union == 0:
        return 0.0
    
    score = (intersection / union) * 100
    return round(score, 2)

def create_rankings_for_resume(resume_id, applicant_id):
    """
    Create ranking entries for a new resume against all active jobs.
    """
    resume = Resume.query.get(resume_id)
    if not resume:
        return
    
    # Get all jobs
    all_jobs = Job.query.all()
    
    for job in all_jobs:
        # Calculate match score
        resume_skills = [s.skill_name for s in resume.skills]
        job_skills = [s.skill_name for s in job.skills]
        score = calculate_match_score(resume_skills, job_skills)
        
        # Check if ranking already exists
        existing_ranking = Ranking.query.filter_by(job_id=job.job_id, resume_id=resume_id).first()
        if existing_ranking:
            existing_ranking.matching_score = score
        else:
            ranking = Ranking(job_id=job.job_id, resume_id=resume_id, matching_score=score)
            db.session.add(ranking)
    
    db.session.commit()

# ============ AUTHENTICATION ROUTES ============

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user (applicant or recruiter)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    name = data.get('name')
    
    if not email or not password or not role:
        return jsonify({"error": "Missing required fields"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 409
    
    if role not in ['applicant', 'recruiter']:
        return jsonify({"error": "Invalid role"}), 400
        
    hashed_password = generate_password_hash(password)
    
    if role == 'applicant':
        new_user = Applicant(email=email, name=name, password_hash=hashed_password, role=role)
    else:
        new_user = Recruiter(email=email, name=name, password_hash=hashed_password, role=role)
        
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user_id": str(new_user.user_id), "role": role}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    """Login and retrieve user credentials"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
        
    return jsonify({
        "message": "Login successful",
        "user_id": str(user.user_id),
        "role": user.role,
        "name": user.name,
        "email": user.email
    }), 200

# ============ PROFILE ROUTES ============

@api.route('/profile/<user_id>', methods=['GET', 'PUT'])
def profile(user_id):
    """Get or update user profile"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if request.method == 'GET':
        result = {
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "phone": user.phone,
            "location": user.location
        }
        if user.role == 'recruiter':
            result.update({
                "company": user.company,
                "job_title": user.job_title
            })
        return jsonify(result), 200
        
    elif request.method == 'PUT':
        data = request.get_json()
        user.name = data.get('name', user.name)
        user.phone = data.get('phone', user.phone)
        user.location = data.get('location', user.location)
        
        if user.role == 'recruiter':
            user.company = data.get('company', user.company)
            user.job_title = data.get('job_title', user.job_title)
            
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

# ============ JOB POSTING ROUTES ============

@api.route('/jobs', methods=['GET', 'POST'])
def jobs():
    """List all jobs or create a new job posting"""
    if request.method == 'POST':
        data = request.get_json()
        recruiter_id = data.get('recruiter_id')
        title = data.get('title')
        skills = data.get('skills', [])
        
        if not recruiter_id or not title:
            return jsonify({"error": "Missing recruiter_id or title"}), 400
        
        # Verify recruiter exists
        recruiter = Recruiter.query.get(recruiter_id)
        if not recruiter:
            return jsonify({"error": "Recruiter not found"}), 404
            
        new_job = Job(recruiter_id=recruiter_id, title=title)
        
        for skill_name in skills:
            if not skill_name.strip():
                continue
            skill = Skill.query.filter_by(skill_name=skill_name.lower()).first()
            if not skill:
                skill = Skill(skill_name=skill_name.lower())
                db.session.add(skill)
            if skill not in new_job.skills:
                new_job.skills.append(skill)
            
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            "message": "Job posted successfully",
            "job_id": str(new_job.job_id),
            "title": new_job.title,
            "skills": [s.skill_name for s in new_job.skills]
        }), 201
        
    elif request.method == 'GET':
        # Pagination
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
                "recruiter_name": job.recruiter.name,
                "created_at": job.created_at.isoformat(),
                "skills": [s.skill_name for s in job.skills]
            } for job in jobs_list]
        }
        
        return jsonify(result), 200

@api.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get details of a specific job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    result = {
        "job_id": str(job.job_id),
        "title": job.title,
        "recruiter_id": str(job.recruiter_id),
        "recruiter_name": job.recruiter.name,
        "recruiter_company": job.recruiter.company,
        "created_at": job.created_at.isoformat(),
        "skills": [s.skill_name for s in job.skills]
    }
    
    return jsonify(result), 200

# ============ RESUME & MATCHING ROUTES ============

@api.route('/resumes', methods=['POST', 'GET'])
def resumes():
    """Upload a new resume or get applicant's resumes"""
    if request.method == 'POST':
        data = request.get_json()
        applicant_id = data.get('applicant_id')
        raw_text = data.get('raw_text', '')
        
        if not applicant_id:
            return jsonify({"error": "Missing applicant_id"}), 400
        
        # Verify applicant exists
        applicant = Applicant.query.get(applicant_id)
        if not applicant:
            return jsonify({"error": "Applicant not found"}), 404
        
        # Extract skills from resume text
        extracted_skills = extract_skills_from_text(raw_text)
        
        # Create resume
        new_resume = Resume(applicant_id=applicant_id, raw_text=raw_text)
        
        # Add extracted skills to resume
        for skill_name in extracted_skills:
            skill = Skill.query.filter_by(skill_name=skill_name.lower()).first()
            if not skill:
                skill = Skill(skill_name=skill_name.lower())
                db.session.add(skill)
            if skill not in new_resume.skills:
                new_resume.skills.append(skill)
        
        db.session.add(new_resume)
        db.session.flush()
        
        # Create rankings for this resume against all jobs
        create_rankings_for_resume(new_resume.resume_id, applicant_id)
        
        db.session.commit()
        
        return jsonify({
            "message": "Resume uploaded successfully",
            "resume_id": str(new_resume.resume_id),
            "skills_extracted": extracted_skills
        }), 201
    
    elif request.method == 'GET':
        applicant_id = request.args.get('applicant_id')
        if not applicant_id:
            return jsonify({"error": "Missing applicant_id"}), 400
        
        resumes_list = Resume.query.filter_by(applicant_id=applicant_id).all()
        
        result = [{
            "resume_id": str(r.resume_id),
            "uploaded_at": r.uploaded_at.isoformat(),
            "skills": [s.skill_name for s in r.skills]
        } for r in resumes_list]
        
        return jsonify(result), 200

@api.route('/applicants/<applicant_id>/matched-jobs', methods=['GET'])
def get_matched_jobs(applicant_id):
    """Get all jobs matched to an applicant's resume with scores"""
    applicant = Applicant.query.get(applicant_id)
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404
    
    # Get most recent resume
    latest_resume = Resume.query.filter_by(applicant_id=applicant_id).order_by(Resume.uploaded_at.desc()).first()
    
    if not latest_resume:
        return jsonify({"error": "No resume found for applicant"}), 404
    
    # Get rankings for this resume
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    
    query = Ranking.query.filter(
        Ranking.resume_id == latest_resume.resume_id,
        Ranking.matching_score >= min_score
    ).order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    result = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "resume_id": str(latest_resume.resume_id),
        "matched_jobs": [{
            "job_id": str(r.job.job_id),
            "title": r.job.title,
            "recruiter_name": r.job.recruiter.name,
            "recruiter_company": r.job.recruiter.company,
            "matching_score": r.matching_score,
            "skills": [s.skill_name for s in r.job.skills]
        } for r in rankings]
    }
    
    return jsonify(result), 200

# ============ RECRUITER CANDIDATE ROUTES ============

@api.route('/jobs/<job_id>/candidates', methods=['GET'])
def get_job_candidates(job_id):
    """Get all candidates for a specific job, ranked by match score"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    
    # Get rankings for this job
    query = Ranking.query.filter(
        Ranking.job_id == job_id,
        Ranking.matching_score >= min_score
    ).order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    result = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "job_id": str(job_id),
        "job_title": job.title,
        "candidates": [{
            "ranking_id": str(r.ranking_id),
            "applicant_id": str(r.resume.applicant_id),
            "applicant_name": r.resume.applicant.name,
            "applicant_email": r.resume.applicant.email,
            "applicant_location": r.resume.applicant.location,
            "matching_score": r.matching_score,
            "candidate_rank": r.candidate_rank,
            "resume_skills": [s.skill_name for s in r.resume.skills]
        } for r in rankings]
    }
    
    return jsonify(result), 200

@api.route('/recruiters/<recruiter_id>/candidates', methods=['GET'])
def get_recruiter_candidates(recruiter_id):
    """Get all candidates for all jobs posted by a recruiter"""
    recruiter = Recruiter.query.get(recruiter_id)
    if not recruiter:
        return jsonify({"error": "Recruiter not found"}), 404
    
    # Get all jobs for this recruiter
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
    
    # Get rankings for all recruiter's jobs
    query = Ranking.query.filter(
        Ranking.job_id.in_(job_ids),
        Ranking.matching_score >= min_score
    ).order_by(Ranking.matching_score.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rankings = pagination.items
    
    result = {
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "recruiter_id": str(recruiter_id),
        "candidates": [{
            "ranking_id": str(r.ranking_id),
            "job_id": str(r.job.job_id),
            "job_title": r.job.title,
            "applicant_id": str(r.resume.applicant_id),
            "applicant_name": r.resume.applicant.name,
            "applicant_email": r.resume.applicant.email,
            "applicant_location": r.resume.applicant.location,
            "matching_score": r.matching_score,
            "candidate_rank": r.candidate_rank,
            "resume_skills": [s.skill_name for s in r.resume.skills]
        } for r in rankings]
    }
    
    return jsonify(result), 200

@api.route('/rankings/<ranking_id>', methods=['PUT'])
def update_ranking(ranking_id):
    """Update candidate ranking/status"""
    ranking = Ranking.query.get(ranking_id)
    if not ranking:
        return jsonify({"error": "Ranking not found"}), 404
    
    data = request.get_json()
    
    if 'candidate_rank' in data:
        ranking.candidate_rank = data.get('candidate_rank')
    
    db.session.commit()
    
    return jsonify({
        "message": "Ranking updated successfully",
        "ranking_id": str(ranking.ranking_id),
        "candidate_rank": ranking.candidate_rank
    }), 200
