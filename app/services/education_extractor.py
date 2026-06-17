import re

EDUCATION_HEADERS = [

    "education",
    "academic background",
    "qualification"
]


def extract_education(text):

    lines = text.split("\n")

    education_section = []

    capture = False

    for line in lines:

        clean_line = line.strip().lower()

        # Detect education section

        if clean_line in EDUCATION_HEADERS:

            capture = True

            continue

        # Stop when next major section starts

        if capture and clean_line in [

            "experience",
            "skills",
            "projects",
            "certifications"
        ]:

            break

        if capture:

            education_section.append(line.strip())

    return education_section
