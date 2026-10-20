from enum import Enum


class AppErrorCode(Enum):
    INVALID_FILE_TYPE = "Unsupported file format"
    FILE_TOO_LARGE = "File size exceeds 4 MB limit"
    FILE_READ_ERROR = "Unable to read file"
    PARSING_ERROR = "Error while parsing file content"
    EMPTY_FILE = "Uploaded file is empty"
