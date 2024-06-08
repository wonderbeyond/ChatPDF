from pypdf import PdfReader


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join(p.extract_text() for p in reader.pages)
