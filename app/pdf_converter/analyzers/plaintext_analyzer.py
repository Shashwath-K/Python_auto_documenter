import os
from app.pdf_converter.analyzers.document_model import StructuredDocument, DocBlock


def analyze_plaintext(content: str, file_path: str) -> StructuredDocument:
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0].replace("_", " ").title()

    blocks = []

    for line in content.splitlines():
        if line.strip():
            blocks.append(DocBlock("paragraph", line.strip()))

    return StructuredDocument(title=title, blocks=blocks)
