import json
from app.utils.extractor import extract_skills
from app.utils.matcher import match_skills
from app.utils.scorer import calculate_score
from app.utils.feedback import generate_feedback

def test_integration():
    resume_data = {
        "candidate_id": 1,
        "skills": ["Python", "SQL"]
    }
    
    job_description = """
    Looking for Python, SQL, AWS skills.
    """
    
    # Extract skills from JD
    job_skills = extract_skills(job_description)
    
    # Match skills
    matched, missing = match_skills(
        resume_data["skills"],
        job_skills
    )
    
    # Score
    score = calculate_score(
        matched,
        job_skills
    )
    
    # Feedback
    feedback = generate_feedback(
        score,
        missing
    )
    
    # Final Output
    result = {
        "candidate_id": 1,
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "feedback": feedback
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_integration()
