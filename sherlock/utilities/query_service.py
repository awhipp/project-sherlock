"""Class which ingests file text into an LLM for query."""

import os
from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from typing import Union

from sherlock.utilities.file_type import print_from_stream
from sherlock.utilities.llm import OllamaClient


class QueryService:
    """Class for ingesting text data into an LLM for query."""

    ollama: OllamaClient = None
    embedding_model: str = "all-minilm"
    llm_model: str = "llama3"

    def __init__(self):
        """Initialize the Ingestion class."""
        self.ollama = OllamaClient()

    def add_document(self, document: str, document_name: str):
        """Add a document to the LLM."""
        self.ollama.add_context(
            context=[document],
            model_name=self.embedding_model,
            collection_name=document_name,
        )

    def query(
        self,
        prompt: str,
        collection_name: str = "default",
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Query the LLM."""
        return self.ollama.prompt_from_context(
            prompt=prompt,
            collection_name=collection_name,
            model_name=self.llm_model,
        )


if __name__ == "__main__":
    # Goes through all txt files in the web_docs folder (and subdirectories)
    # and populates the documents then queries the LLM.

    print("-- Creating Query Service --")
    client = QueryService()

    print("-- Adding Documents --")
    for root, dirs, files in os.walk("web_docs"):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    print(f"-- Adding {file} --")
                    client.add_document(document=f.read(), document_name=file)

    print("-- Querying LLM --")
    print_from_stream(
        client.query(prompt="What is the Colorado ICAP?", collection_name="icap.txt"),
        key="response",
    )
