import pytest
from fastapi.testclient import TestClient
from calculator.main import app


client = TestClient(app)


def test_add():
    resp = client.post("/add", json={"a": 1.5, "b": 2.5})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(4.0)


def test_subtract():
    resp = client.post("/subtract", json={"a": 5.0, "b": 3.0})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(2.0)


def test_multiply():
    resp = client.post("/multiply", json={"a": 2.0, "b": 4.0})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(8.0)


def test_divide():
    resp = client.post("/divide", json={"a": 10.0, "b": 2.0})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(5.0)


def test_divide_by_zero():
    resp = client.post("/divide", json={"a": 10.0, "b": 0.0})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Division by zero"

