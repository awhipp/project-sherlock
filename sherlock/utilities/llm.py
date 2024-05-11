"""Utilities to control the LLM UI related functions."""

import ollama


class OllamaClient:
    """Singleton class to interact with the Ollama LLM server."""

    _instance = None

    host: str = "127.0.0.1"
    port: str = "11434"
    client: ollama.Client = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.client is None:
            self.client = ollama.Client(host=f"{self.host}:{self.port}")

    def list_models(self):
        """List all the available models."""
        return self.client.list()["models"]

    def get_model(self, model_name: str):
        """Get the model by name."""
        try:
            steam = self.client.pull(model_name, stream=True)

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
        stream = self.client.chat(
            model=model_name,
            messages=[{"role": "user", "content": text}],
            stream=True,
        )

        all_chunks = []

        for chunk in stream:
            all_chunks.append(chunk["message"]["content"])
            print(chunk["message"]["content"], end="", flush=True)

        return all_chunks

    def embed(self, text: str, model_name: str = "all-minilm"):
        """Embed the text using the model."""
        embeddings_object = self.client.embeddings(model=model_name, prompt=text)

        if "embeddings" in embeddings_object:
            return embeddings_object["embeddings"]
        else:
            return []


if __name__ == "__main__":
    client = OllamaClient()
    # client.client.delete("llama3")
    # client.get_model("llama3")
    # client.get_model("all-minilm")
    # print(
    #     client.list_models()
    # )
    embeddings = client.embed("Sherlock Homey.")
    client.chat("llama3", f"Embeddings:{embeddings}, Question:What's my name?")
