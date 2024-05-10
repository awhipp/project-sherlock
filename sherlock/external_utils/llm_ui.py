"""Utilities to control the LLM UI related functions."""

import requests


def sync_documents():
    """Sync the documents from the LLM server."""
    # TODO - Add the username and password for the LLM server and determine credentials
    username = ""
    password = ""
    url = "http://localhost:3000/rag/api/v1/scan"

    response = requests.get(url, auth=(username, password), timeout=30)
    print(response.status_code)
    print(response.content)
    # if response.status_code == 200:
    #     print("Documents synced successfully.")
    # else:
    #     print("Failed to sync documents.")


if __name__ == "__main__":
    sync_documents()
