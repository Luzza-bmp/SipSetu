import fitz


def extract_pdf_text(filepath):

    text = ""

    pdf = fitz.open(filepath)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text
