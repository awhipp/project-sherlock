"""Utilities to control the LLM UI related functions."""

from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from typing import Union

import chromadb as cdb
import ollama as ollm
from tqdm import tqdm


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
        response = self.ollama.list()
        if "models" not in response:
            return []
        elif isinstance(response["models"], list):
            return response["models"]
        else:
            return []

    def get_model(self, model_name: str):
        """Get the model by name."""
        current_digest, bars = "", {}
        for progress in self.ollama.pull(model_name, stream=True):
            digest = progress.get("digest", "")
            if digest != current_digest and current_digest in bars:
                bars[current_digest].close()

            if not digest:
                print(progress.get("status"))
                continue

            if digest not in bars and (total := progress.get("total")):
                bars[digest] = tqdm(
                    total=total,
                    desc=f"pulling {digest[7:19]}",
                    unit="B",
                    unit_scale=True,
                )

            if completed := progress.get("completed"):
                bars[digest].update(completed - bars[digest].n)

            current_digest = digest

        return self.list_models()

    def remove_model(self, model_name: str):
        """Remove the model by name."""
        response = self.ollama.delete(model=model_name)
        return response["status"] == "success"

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
