import pytest
from fastapi.testclient import TestClient

from calculator.main import app


client = TestClient(app)


def test_add():
    resp = client.post("/add", json={"a": 1.5, "b": 2.5})
    assert resp.status_code == 200
    assert resp.json() == {"result": 4.0}


def test_subtract():
    resp = client.post("/subtract", json={"a": 5, "b": 3})
    assert resp.status_code == 200
    assert resp.json() == {"result": 2}


def test_multiply():
    resp = client.post("/multiply", json={"a": 2, "b": 4.5})
    assert resp.status_code == 200
    assert resp.json() == {"result": 9.0}


def test_divide():
    resp = client.post("/divide", json={"a": 9, "b": 3})
    assert resp.status_code == 200
    assert resp.json() == {"result": 3}


def test_divide_by_zero_returns_400():
    resp = client.post("/divide", json={"a": 1, "b": 0})
    assert resp.status_code == 400
    assert resp.json()["detail"]

