from pypdf import PdfReader
from io import BytesIO
from docx import Document


def extract_pdf(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text



def extract_docx(file_bytes):
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)