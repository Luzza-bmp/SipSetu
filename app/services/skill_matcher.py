import re

SKILLS_DB = {
    "python",
    "java",
    "c++",
    "sql",
    "postgresql",
    "mysql",
    "nosql",
    "javascript",
    "c#",
    "c",
    "html",
    "html5",
    "css",
    "api",
    "excel",
    "ms-word",
    "ms-excel",
    "flutter",
    "pyspark",
    "mongodb",
    "flask",
    "django",
    "react",
    "reactjs",
    "nextjs",
    "nodejs",
    "angularjs",
    "matplotlib",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "natural language processing",
    "data science",
    "data mining",
    "data analysis",
    "pandas",
    "numpy",
    "tableau",
    "power bi",
    "git",
    "docker",
}


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))
