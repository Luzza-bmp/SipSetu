from app.services.pdf_parser import extract_pdf_text
from app.services.docx_parser import extract_docx_text

from app.services.info_extractor import (
    extract_name,
    extract_email,
    extract_phone
)

from app.services.skill_matcher import extract_skills

from app.services.education_extractor import (
    extract_education
)

from app.services.experience_extractor import (
    extract_experience_years
)


def parse_resume(filepath):

    if filepath.endswith(".pdf"):
        text = extract_pdf_text(filepath)

    elif filepath.endswith(".docx"):
        text = extract_docx_text(filepath)

    else:
        return {"error": "Unsupported file format"}

    parsed_data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "education": extract_education(text),

        "experience": extract_experience_years(text),

    }

    return parsed_data
