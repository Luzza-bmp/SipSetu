import re


def parse_experience(experience_lines):

    parsed_experience = []

    for line in experience_lines:

        line = line.strip()

        # Skip empty lines

        if not line:
            continue

        # Skip bullet points

        if line.startswith("•") or line.startswith(""):
            continue

        exp = {
            "role": None,
            "company": None
        }

        # Detect company/date lines

        if "," in line:

            exp["company"] = line

        else:

            exp["role"] = line

        # Append only valid entries

        if exp["role"] or exp["company"]:

            parsed_experience.append(exp)

    return parsed_experience
