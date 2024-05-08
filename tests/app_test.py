"""Application test for the fastapi app"""

from fastapi.testclient import TestClient

from sherlock.app import app


def test_home():
    """Test the home route."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello, World!"
