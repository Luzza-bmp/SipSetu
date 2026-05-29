def parse_education(education_lines):

    parsed_education = []

    for line in education_lines:

        line = line.strip()

        if not line:
            continue

        edu = {
            "degree": None,
            "institution": None
        }

        lower = line.lower()

        # Detect degrees

        if (
            "bachelor" in lower
            or "bsc" in lower
            or "be" in lower
            or "b.tech" in lower
            or "computer science" in lower
        ):

            edu["degree"] = line

        # Detect institutions

        elif (
            "university" in lower
            or "college" in lower
            or "school" in lower
        ):

            edu["institution"] = line

        # ONLY append if at least one field exists

        if edu["degree"] or edu["institution"]:

            parsed_education.append(edu)

    return parsed_education
