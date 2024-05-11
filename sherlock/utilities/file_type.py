"""File Type Enum Class"""

from enum import Enum


class FileType(Enum):
    """File Type Enum Class"""

    HTML = "Web Page (HTML)"
    PDF = "PDF"
    DOCX = "Word Document (DOCX)"
    XLSX = "Excel / Spreadsheet Document (XLSX)"
    CSV = "CSV"
    PPTX = "PowerPoint Document (PPTX)"
    Unsupported = "Unsupported"

    def __str__(self):
        return self.value
