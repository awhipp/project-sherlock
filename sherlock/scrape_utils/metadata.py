"""Metadata model to add to the top of all documents."""


from pydantic import BaseModel

from sherlock.file_utils.file_type import FileType

class Metadata(BaseModel):
    """Metadata model to add to the top of all documents."""

    title: str
    source: str
    file_type: FileType
    retrieved_date: str

    def to_markdown(self):
        """Convert the metadata to a markdown string."""
        metadata = "# Metadata for this file:\n\n"

        for key, value in self.model_dump().items():
            metadata += f"\n- {key}: {value}"

        metadata += "\n\n** END OF METADATA **\n\n"

        return metadata