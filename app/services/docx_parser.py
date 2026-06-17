from docx import Document


def extract_docx_text(filepath):

    doc = Document(filepath)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text
