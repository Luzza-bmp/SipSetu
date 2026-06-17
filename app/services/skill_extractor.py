SKILLS_DB = [

    "Python",
    "Java",
    "JavaScript",
    "Flask",
    "Django",
    "React",
    "Node.js",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "Docker",
    "AWS",
    "Git",
    "HTML",
    "CSS",
    "C++"
]


def extract_skills(text):

    found_skills = []

    text = text.lower()

    for skill in SKILLS_DB:

        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))
