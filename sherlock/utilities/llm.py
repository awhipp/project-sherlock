"""Utilities to control the LLM UI related functions."""

from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from typing import Union

import chromadb as cdb
import ollama as ollm


class OllamaClient:
    """Singleton class to interact with the Ollama LLM server."""

    _instance = None

    host: str = "127.0.0.1"
    port: str = "11434"
    ollama: ollm.Client = None
    chromadb: cdb.Client = None
    collections: dict[str, cdb.Collection] = {}
    last_index: dict[str, int] = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.ollama is None:
            self.ollama = ollm.Client(host=f"{self.host}:{self.port}")
        if self.chromadb is None:
            self.chromadb = cdb.Client()
            self.collections["default"] = self.chromadb.create_collection(
                name="default",
            )
            self.last_index["default"] = 0

    def list_models(self):
        """List all the available models."""
        if "models" not in self.ollama.list():
            return []
        else:
            return self.ollama.list()["models"]

    def get_model(self, model_name: str):
        """Get the model by name."""
        try:
            steam = self.ollama.pull(model_name, stream=True)

            has_completed = False

            for message in steam:
                if message["status"] == "pulling manifest":
                    print(f"Pulling manifest for model {model_name}.")
                elif "pulling" in message["status"] and "completed" in message:
                    total = int(message["total"])
                    current = int(message["completed"])
                    percentage = f"{(current / total) * 100:.2f}%"
                    if not has_completed:
                        print(f"Downloading model {model_name}: {percentage}")
                    if percentage == "100.00%":
                        has_completed = True
                elif "verifying" in message["status"]:
                    print(f"Verifying model {model_name}.")
                elif "writing" in message["status"]:
                    print(f"Writing model {model_name}.")
                elif "success" in message["status"]:
                    print(f"Model {model_name} downloaded successfully.")
                elif "removing any unused layers" in message["status"]:
                    print("Cleaning up...")

            return self.list_models()

        except Exception:
            print(f"Model {model_name} not found.")

    def chat(self, model_name: str, text: str):
        """Chat with the model."""
        stream = self.ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": text}],
            stream=True,
        )

        all_chunks = []

        for chunk in stream:
            all_chunks.append(chunk["message"]["content"])
            print(chunk["message"]["content"], end="", flush=True)

        return all_chunks

    def add_context(
        self,
        context: list[str],
        model_name: str = "all-minilm",
        collection_name: str = "default",
    ):
        """Embed the text using the model."""
        # store each document in a vector embedding database
        for _, c in enumerate(context):
            embedding = self.embeddings(model_name=model_name, prompt=c)

            if len(embedding) == 0:
                continue

            if collection_name not in self.collections:
                self.collections[collection_name] = self.chromadb.create_collection(
                    name=collection_name,
                )
                self.last_index[collection_name] = 0

            self.collections[collection_name].add(
                ids=[str(self.last_index[collection_name])],
                embeddings=[embedding],
                documents=[c],
            )
            self.last_index[collection_name] += 1

            # add the same document to the default collection
            if collection_name != "default":
                self.collections["default"].add(
                    ids=[str(self.last_index["default"])],
                    embeddings=[embedding],
                    documents=[c],
                )
                self.last_index["default"] += 1

    def embeddings(self, prompt: str, model_name: str = "all-minilm"):
        """Embed the text using the model."""
        response = self.ollama.embeddings(model=model_name, prompt=prompt)
        return response["embedding"]

    def prompt_from_context(
        self,
        prompt: str,
        model_name: str = "llama3",
        collection_name: str = "default",
    ) -> Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]:
        """Prompt with context."""

        # generate an embedding for the prompt and retrieve the most relevant doc
        embedding = self.embeddings(
            prompt=prompt,
        )
        results = self.collections[collection_name].query(
            query_embeddings=[embedding],
            n_results=1,
        )
        data = results["documents"][0][0]

        return self.ollama.generate(
            model=model_name,
            prompt=f"Using this data: {data}. Respond to the prompt: {prompt}",
            stream=True,
        )
