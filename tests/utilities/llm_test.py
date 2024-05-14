"""Test the LLM Client."""

from sherlock.utilities.file_type import print_from_stream
from sherlock.utilities.llm import OllamaClient as client


def test_llm_client_singleton():
    """Test the LLM Client Singleton."""
    c1 = client()
    c2 = client()
    assert c1 == c2


def test_llm_client_list_models():
    """Test the LLM Client List Models."""
    c = client()
    models = c.list_models()
    assert isinstance(models, list)
    assert len(models) >= 0


def test_llm_prompt_with_context():
    """Prompts a query with context for the LLM."""
    ollama = client()

    ollama.add_context(
        context=["My cat is named catherine.", "My dog is charles barkley."],
    )

    result = print_from_stream(
        ollama.prompt_from_context(
            prompt="What is my dog's name?",
        ),
        key="response",
    )

    assert "Charles Barkley" in result
