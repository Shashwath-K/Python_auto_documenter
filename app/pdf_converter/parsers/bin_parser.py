from app.pdf_converter.exceptions.custom_exceptions import ParsingError
from app.pdf_converter.enums.error_codes import AppErrorCode


def parse_bin(file):
    """
    Parses binary file by decoding bytes safely.
    Non-decodable bytes are ignored.
    """
    try:
        with open(file.name, "rb") as f:
            return f.read().decode("utf-8", errors="ignore")
    except Exception:
        raise ParsingError(AppErrorCode.PARSING_ERROR.value)
