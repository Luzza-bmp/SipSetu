import re
import spacy


nlp = spacy.load("en_core_web_sm")


def extract_name(text):

    doc = nlp(text[:1000])

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            return ent.text

    return None


def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    matches = re.findall(pattern, text)

    return matches[0] if matches else None


def extract_phone(text):

    pattern = r"""
    (?:
        \+?\d{1,3}[\s\-]?
    )?
    (?:\(?\d{3}\)?[\s\-]?)?
    \d{3}[\s\-]?\d{4}
    """

    matches = re.findall(pattern, text, re.VERBOSE)

    cleaned_numbers = []

    for number in matches:

        cleaned = re.sub(r"\D", "", number)

        if len(cleaned) >= 10:
            cleaned_numbers.append(cleaned)

    return cleaned_numbers[0] if cleaned_numbers else None
