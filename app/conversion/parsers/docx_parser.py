from docx import Document
from app.conversion.exceptions.custom_exceptions import ParsingError
from app.conversion.enums.error_codes import AppErrorCode


def parse_docx(file):
    """
    Extracts text from a DOCX file.
    """
    try:
        document = Document(file.name)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        raise ParsingError(AppErrorCode.PARSING_ERROR.value)
