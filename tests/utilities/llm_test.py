"""Test the LLM Client."""

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
    assert models == [] or models is None
