class FileValidationError(Exception):
    """
    Raised when file validation fails.
    Examples:
    - Unsupported file type
    - File size exceeded
    - Empty file
    """

    def __init__(self, message: str):
        super().__init__(message)


class ParsingError(Exception):
    """
    Raised when file content cannot be parsed correctly.
    """

    def __init__(self, message: str):
        super().__init__(message)
