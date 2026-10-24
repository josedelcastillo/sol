import pytest
from fastapi.testclient import TestClient

from app import inventory
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_inventory(monkeypatch):
    monkeypatch.delenv("NOTIFY_WEBHOOK_URL", raising=False)
    inventory.reset()
    yield
    inventory.reset()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_items():
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    for item in items:
        assert set(item) == {"id", "name", "qty"}


def test_withdraw_ok():
    response = client.post("/items/2/withdraw", json={"qty": 3})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Monitor", "qty": 5}


def test_withdraw_exact_stock():
    response = client.post("/items/1/withdraw", json={"qty": 5})
    assert response.status_code == 200
    assert response.json()["qty"] == 0


def test_withdraw_exceeds_stock():
    response = client.post("/items/1/withdraw", json={"qty": 6})
    assert response.status_code == 400


def test_withdraw_not_found():
    response = client.post("/items/999/withdraw", json={"qty": 1})
    assert response.status_code == 404


def test_debug_config():
    response = client.get("/debug/config")
    assert response.status_code == 200
    assert isinstance(response.json()["api_key_configured"], bool)
