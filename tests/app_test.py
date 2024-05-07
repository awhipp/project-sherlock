"""Application test for the flask app"""

from sherlock.app import app


def test_home_route():
    """Test the home route."""
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.data == b"Hello, World!"
