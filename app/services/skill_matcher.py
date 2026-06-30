import re

SKILLS_DB = {
    "python",
    "java",
    "c++",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "flask",
    "django",
    "react",
    "nodejs",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data analysis",
    "pandas",
    "numpy",
    "tableau",
    "power bi",
    "git",
    "docker"
}


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))
