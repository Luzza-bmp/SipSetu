SECTION_HEADERS = [

    "education",
    "skills",
    "skills / strengths",
    "experience",
    "projects",
    "activities",
    "certifications"
]


def detect_sections(text):

    lines = text.split("\n")

    sections = {}

    current_section = "other"

    sections[current_section] = []

    for line in lines:

        clean_line = line.strip().lower()

        # Detect section header

        matched = False

        for header in SECTION_HEADERS:

            if clean_line == header:

                current_section = header

                sections[current_section] = []

                matched = True

                break

        if not matched:

            sections[current_section].append(line.strip())

    return sections
