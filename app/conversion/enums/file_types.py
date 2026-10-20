from enum import Enum


class SupportedFileType(Enum):
    BIN = "bin"
    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    CSV = "csv"
    HTML = "html"
    IPYNB = "ipynb"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]
