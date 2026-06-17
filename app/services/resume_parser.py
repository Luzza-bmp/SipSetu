from app.services.pdf_parser import extract_pdf_text
from app.services.docx_parser import extract_docx_text

from app.services.info_extractor import (
    extract_name,
    extract_email,
    extract_phone
)

from app.services.skill_extractor import extract_skills

from app.services.education_extractor import extract_education
from app.services.experience_extractor import extract_experience
from app.services.project_extractor import extract_projects
from app.services.section_detector import detect_sections

from app.services.link_extractor import extract_links

# Import parsers

from app.services.parsers.education_parser import parse_education
from app.services.parsers.experience_parser import parse_experience
from app.services.parsers.project_parser import parse_projects


def parse_resume(filepath):

    # Extract text

    if filepath.endswith(".pdf"):

        text = extract_pdf_text(filepath)

    elif filepath.endswith(".docx"):

        text = extract_docx_text(filepath)

    else:

        return {"error": "Unsupported file format"}

    sections = detect_sections(text)

    # Extract sections first

    education_lines = sections.get("education", [])

    experience_lines = sections.get("experience", [])

    project_lines = sections.get("projects", [])

    # Parse sections into structured objects

    parsed_education = parse_education(education_lines)

    parsed_experience = parse_experience(experience_lines)

    parsed_projects = parse_projects(project_lines)

    # Final structured response

    parsed_data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "education": parsed_education,

        "experience": parsed_experience,

        "projects": parsed_projects,

        "links": extract_links(text)
    }

    return parsed_data
