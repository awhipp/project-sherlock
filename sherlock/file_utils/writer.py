"""Writer utility functions."""

import os


S = os.sep

INVALID_DIR_FILE_CHARS = ["\\", ":", "?", "*", '"', "<", ">", "|"]


def ensure_dir_file_name_valid(name: str) -> str:
    """Ensure that a directory or file name is valid.

    Args:
    name (str): The name of the directory or file.

    Returns:
    str: The valid directory or file name.
    """

    if "https" in name:
        name = name.replace("https://", "")
    if "http" in name:
        name = name.replace("http://", "")

    if "/" in name:
        name = name.replace("/", " ")

    for char in INVALID_DIR_FILE_CHARS:
        name = name.replace(char, "")
    return name


ROOT_PATH = "web_docs"


def write_file(base_url: str, sub_url: str, content: str) -> int:
    """Write a text file to a given directory.

    The directory is created if it does not exist.
    - The base_url represents the root directory,
    - The sub_url is the file name (.txt)
    - The content is the text to write.

    The root of the root directory is a data directory in the current working directory.

    Args:
    base_url (str): The base URL of the website.
    sub_url (str): The sub-URL of the website.
    content (str): The content to write to the file.

    Returns the total file size for the base_url directory.
    """
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)

    base_url = ensure_dir_file_name_valid(base_url)
    if not os.path.exists(f"{ROOT_PATH}{S}{base_url}"):
        os.makedirs(f"{ROOT_PATH}{S}{base_url}")

    sub_url = ensure_dir_file_name_valid(sub_url)
    with open(
        f"{ROOT_PATH}{S}{base_url}{S}{sub_url}.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(content)

    return sum(
        os.path.getsize(f"{ROOT_PATH}{S}{base_url}{S}{file}")
        for file in os.listdir(f"{ROOT_PATH}{S}{base_url}")
    )