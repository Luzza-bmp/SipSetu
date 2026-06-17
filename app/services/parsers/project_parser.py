def parse_projects(project_lines):

    parsed_projects = []

    for line in project_lines:

        line = line.strip()

        if not line:
            continue

        if line.startswith("•") or line.startswith(""):
            continue

        project = {
            "title": line,
            "technologies": []
        }

        parsed_projects.append(project)

    return parsed_projects
