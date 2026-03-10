import os

from app.pdf_converter.enums.file_types import SupportedFileType
from app.pdf_converter.enums.error_codes import AppErrorCode
from app.pdf_converter.exceptions.custom_exceptions import FileValidationError
from app.pdf_converter.utils.constants import MAX_FILE_SIZE


def validate_file(file):
    """
    Validates uploaded file from Gradio.
    """

    if file is None:
        raise FileValidationError("No file uploaded")

    # Gradio provides a temp file object with `.name` as file path
    if not hasattr(file, "name"):
        raise FileValidationError("Invalid file object")

    file_path = file.name

    if not os.path.exists(file_path):
        raise FileValidationError("Uploaded file not found on disk")

    file_size = os.path.getsize(file_path)

    if file_size == 0:
        raise FileValidationError(AppErrorCode.EMPTY_FILE.value)

    if file_size > MAX_FILE_SIZE:
        raise FileValidationError(AppErrorCode.FILE_TOO_LARGE.value)

    extension = file_path.split(".")[-1].lower()

    if extension not in SupportedFileType.list_values():
        raise FileValidationError(AppErrorCode.INVALID_FILE_TYPE.value)

    return SupportedFileType(extension)
