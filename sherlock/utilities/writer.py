"""Writer utility functions."""

import os
import re
from typing import Union

from sherlock.utilities.file_type import FileType


S = os.sep


def remove_prefix(name: str) -> str:
    """Removes http(s) and www from name

    Args:
    name (str): The name of the directory or file.

    Returns:
    str: The valid directory or file name.
    """
    if "https" in name:
        name = name.replace("https://", "")
    if "http" in name:
        name = name.replace("http://", "")
    if "www." in name:
        name = name.replace("www.", "")
    return name


def path_to_valid_name(name: str) -> str:
    """Ensure that URL path is valid for a directory or file name.

    Args:
    name (str): The name of the directory or file.

    Returns:
    str: The valid directory or file name.
    """
    # Replace URL reserved characters
    # Define a list of characters not allowed in filenames.
    invalid_chars = r'\\/:*?"<>|'

    # Use regex to replace invalid characters with underscore
    valid_filename = re.sub(rf"[{invalid_chars}]", "", name)

    # Strip leading and trailing whitespaces, and normalize spaces
    valid_filename = valid_filename.strip()
    # valid_filename = re.sub(r"\s+", "", valid_filename)

    return valid_filename


ROOT_PATH = "web_docs"


def write_file(
    collection_name: str,
    url: str,
    content: Union[str, bytes],
    file_type: FileType,
    depth: int,
) -> int:
    """Write a text file to a given subdirectory based on the URL.

    Args:
        collection_name (str): The name of the collection.
        url (str): The URL of the website.
        content (Union[str, bytes]): The content to write to the file.
        file_type (FileType): The type of file to write.
        depth (int): The depth of the URL.

    Returns:
        int: The number of characters written to the file.
    """
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)

    url = remove_prefix(url)
    collection_name = remove_prefix(collection_name)
    collection_name = path_to_valid_name(collection_name)

    landing_path = ROOT_PATH + S + collection_name

    if not os.path.exists(landing_path):
        os.makedirs(landing_path)

    url_split = url.split("/")

    if file_type == FileType.HTML:
        file_path = f"{landing_path}{S}{path_to_valid_name(url_split[-1])}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    elif file_type == FileType.DOCX:
        file_path = f"{landing_path}{S}{path_to_valid_name(url_split[-1])}.docx"
        with open(file_path, "wb") as f:
            f.write(content)
    elif file_type == FileType.PDF:
        file_path = f"{landing_path}{S}{path_to_valid_name(url_split[-1])}.pdf"
        with open(file_path, "wb") as f:
            f.write(content)
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    print(f"Scraped: {url} ({file_type} - {len(content)} characters - Depth: {depth})")

    return len(content)
