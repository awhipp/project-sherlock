"""Writer utility functions."""

import os
import re


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


def write_file(url: str, content: str) -> int:
    """Write a text file to a given subdirectory based on the URL.

    For instance if the URL is https://www.example.com/page/example/help.txt
    * `The help.txt` file will be saved in `web_docs` under `example.com/page/example`.

    Args:
    url (str): The URL of the website.
    content (str): The content to write to the file.

    Returns the total file size for the base_url directory.
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

    file_path = f"{running_path}{S}{path_to_valid_name(url_split[-1])}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return 0
