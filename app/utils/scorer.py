def calculate_score(matched, job_skills):
    if not job_skills or len(job_skills) == 0:
        return 0
        
    score = (len(matched) / len(job_skills)) * 100
    return round(score)
