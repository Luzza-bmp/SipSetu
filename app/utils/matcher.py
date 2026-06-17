def match_skills(resume_skills, job_skills):
    matched = []
    missing = []
    
    # Normalize resume skills for lookup
    resume_skills_lower = [s.lower() for s in resume_skills]
    
    for skill in job_skills:
        if skill.lower() in resume_skills_lower:
            matched.append(skill)
        else:
            missing.append(skill)
            
    return matched, missing
