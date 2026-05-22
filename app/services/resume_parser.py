import os

from app.services.pdf_parser import extract_pdf_text
from app.services.docx_parser import extract_docx_text


def parse_resume(filepath):

    extension = os.path.splitext(filepath)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(filepath)

    elif extension == ".docx":
        return extract_docx_text(filepath)

    else:
        return "Unsupported file format"
