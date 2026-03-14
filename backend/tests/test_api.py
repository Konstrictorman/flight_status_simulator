"""Integration tests for flight API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    """Test client with in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_flight(client: TestClient):
    """POST /flights creates a flight and returns 201."""
    r = client.post("/flights")
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["route"] == "LAX-JFK"
    assert data["status"] == "active"


def test_list_flights(client: TestClient):
    """GET /flights returns all flights."""
    client.post("/flights")
    client.post("/flights")
    r = client.get("/flights")
    assert r.status_code == 200
    data = r.json()
    assert "flights" in data
    assert len(data["flights"]) == 2


def test_get_flight(client: TestClient):
    """GET /flights/{id} returns flight with current metrics."""
    create = client.post("/flights")
    flight_id = create.json()["id"]
    r = client.get(f"/flights/{flight_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == flight_id
    assert data["status"] == "active"
    assert "metrics" in data
    m = data["metrics"]
    assert "phase" in m
    assert "altitude_ft" in m
    assert "airspeed_knots" in m
    assert "latitude" in m
    assert "longitude" in m
    assert "fuel_remaining_gal" in m
    assert "eta_seconds" in m


def test_get_flight_404(client: TestClient):
    """GET /flights/{id} returns 404 for unknown flight."""
    r = client.get("/flights/nonexistent-id")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_get_flight_history(client: TestClient):
    """GET /flights/{id}/history returns metric history."""
    create = client.post("/flights")
    flight_id = create.json()["id"]
    r = client.get(f"/flights/{flight_id}/history")
    assert r.status_code == 200
    data = r.json()
    assert data["flight_id"] == flight_id
    assert "history" in data
    assert len(data["history"]) >= 1  # At least initial metric recorded


def test_get_flight_history_404(client: TestClient):
    """GET /flights/{id}/history returns 404 for unknown flight."""
    r = client.get("/flights/nonexistent-id/history")
    assert r.status_code == 404


def test_stream_flight_404(client: TestClient):
    """GET /flights/{id}/stream returns 404 for unknown flight."""
    r = client.get("/flights/nonexistent-id/stream")
    assert r.status_code == 404
