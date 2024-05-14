"""File helper classes and functions"""

from collections.abc import Iterator
from collections.abc import Mapping
from enum import Enum
from typing import Any
from typing import Optional
from typing import Union


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


def print_from_stream(
    stream: Union[Iterator[Mapping[str, Any]], list[Mapping[str, Any]]],
    key: Optional[str] = None,
) -> str:
    """Prints the output from a stream."""

    result = ""

    for message in stream:
        if key is not None and key in message:
            print(message[key], end="", flush=True)
            result += message[key]
        else:
            print(message, end="", flush=True)
            result += message

    return result
