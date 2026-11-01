# Imports
from fastapi.testclient import TestClient

from lonzo.main import app


# Global variables
client = TestClient(app)


# Code
def test_health() -> None:

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
