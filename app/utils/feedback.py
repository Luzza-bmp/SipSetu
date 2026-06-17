def generate_feedback(score, missing_skills):
    feedback = []
    
    if score >= 80:
        feedback.append("Excellent match for this job.")
    elif score >= 60:
        feedback.append("Good match but can improve.")
    else:
        feedback.append("Low match. Improve required skills.")
        
    if missing_skills:
        feedback.append(f"Missing skills: {', '.join(missing_skills)}")
        
    return feedback
