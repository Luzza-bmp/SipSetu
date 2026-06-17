PROJECT_KEYWORDS = [

    "project",
    "developed",
    "built",
    "created",
    "designed"
]


def extract_projects(text):

    projects = []

    lines = text.split("\n")

    for line in lines:

        for keyword in PROJECT_KEYWORDS:

            if keyword.lower() in line.lower():

                projects.append(line.strip())

    return list(set(projects))
