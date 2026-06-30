import re

# Compiled patterns for better performance
# Order matters if you want to extract the highest degree first (PhD down to High School)
EDUCATION_PATTERNS = {
    "PhD": [
        r"\bph\.?d\b",
        r"\bdoctor of philosophy\b",
        r"\bdoctorate\b"
    ],

    "Master's": [
        r"\bmaster(?:'s)?\b",
        r"\bm\.?tech\b",
        # Negative lookahead to avoid "be" edge cases if word boundary misbehaves
        r"\bm\.?e\b(?!\s+ble)",
        r"\bm\.?sc\b",
        r"\bm\.?b\.?a\b",
        # Avoid matching "ms." or "ms" as a title by ensuring it's a standalone uppercase/specific context,
        # or handle it by excluding common contexts.
        r"\bm\.?s\b(?!\.)"
    ],

    "Bachelor's": [
        r"\bbachelor(?:'s)?\b",
        r"\bb\.?tech\b",
        r"\bb\.?e\b",
        r"\bb\.?sc\b",
        r"\bb\.?c\.?a\b",
        r"\bb\.?b\.?a\b",
        r"\bb\.?s\b"
    ],

    "Diploma": [
        r"\bdiploma\b",
        r"\bpolytechnic\b"
    ],

    "High School": [
        r"\bhigh\s?school\b",
        r"\bsecondary education\b",
        r"\bssc\b",
        r"\bhsc\b",
        r"\b10th\b",
        r"\b12th\b"
    ]
}


def extract_education(text):
    # Standardize spaces but keep case for a crucial trick: distinguishing "BE" / "MS" from "be" / "ms"
    text_clean = " ".join(text.split())

    found = []

    for level, patterns in EDUCATION_PATTERNS.items():
        for pattern in patterns:
            # Crucial Fix: For short words like 'be' or 'ms', we check if they were originally capitalized
            # or match them strictly. To keep it simple with your lowercase approach, we use strict boundaries.
            if re.search(pattern, text_clean, re.IGNORECASE):

                # Dynamic false-positive filter for the infamous "to be" vs "B.E." (Bachelor of Engineering)
                if pattern == r"\bb\.?e\b" and re.search(r"\b(to be|will be|should be|must be)\b", text_clean, re.IGNORECASE):
                    # If it looks like a verb phrase, verify it isn't just the standalone lowercase word "be"
                    if " b.e. " not in text_clean.lower() and "be " in text_clean.lower():
                        continue

                # Dynamic false-positive filter for "ms" (title) vs "M.S."
                if pattern == r"\bm\.?s\b(?!\.)" and re.search(r"\b(ms\.\s+[A-Z]|miss)\b", text_clean, re.IGNORECASE):
                    continue

                found.append(level)
                break  # Move to the next education level once a match is found for this tier

    return found
