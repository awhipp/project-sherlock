"""Writer utility functions."""

import os
import re
from typing import Union

from sherlock.utilities.file_type import FileType


S = os.sep


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
    valid_filename = re.sub(r"\s+", "", valid_filename)

    return valid_filename


ROOT_PATH = "web_docs"


def write_file(url: str, content: Union[str, bytes], file_type: FileType) -> int:
    """Write a text file to a given subdirectory based on the URL.

    For instance if the URL is https://www.example.com/page/example/help.txt
    * `The help.txt` file will be saved in `web_docs` under `example.com/page/example`.

    Args:
        url (str): The URL of the website.
        content (Union[str, bytes]): The content to write to the file.
        file_type (FileType): The type of file to write.

    Returns:
        int: The number of characters written to the file.
    """
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)

    if "https" in url:
        url = url.replace("https://", "")
    if "http" in url:
        url = url.replace("http://", "")
    if "www." in url:
        url = url.replace("www.", "")

    url_split = url.split("/")

    running_path = ROOT_PATH
    for idx, part in enumerate(url_split):
        if idx == len(url_split) - 1:
            break
        running_path = f"{running_path}{S}{part}"
        if not os.path.exists(running_path):
            os.makedirs(running_path)

    # ! TODO - Figure out a better naming convention
    if file_type == FileType.HTML:
        file_path = f"{running_path}{S}{path_to_valid_name(url_split[-1])}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    elif file_type == FileType.DOCX:
        file_path = f"{running_path}{S}{path_to_valid_name(url_split[-1])}.docx"
        with open(file_path, "wb") as f:
            f.write(content)
    elif file_type == FileType.PDF:
        file_path = f"{running_path}{S}{path_to_valid_name(url_split[-1])}.pdf"
        with open(file_path, "wb") as f:
            f.write(content)
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    print(f"Scraped: {url} ({file_type} - {len(content)} characters)")

    return len(content)
