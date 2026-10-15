import os
import tempfile
import pytest
import app as application

@pytest.fixture()
def client(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr(application, "DB_PATH", path)
    application.init_db()
    with application.app.test_client() as client:
        yield client
    os.remove(path)

def test_booking_is_created(client):
    response = client.post("/api/bookings", json={
        "passenger_name": "Ayaan Qureshi",
        "email": "ayaan@example.com",
        "route": "Delhi - Jaipur",
        "travel_date": "2026-12-01",
        "seats": 2
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "CONFIRMED"
    assert data["total_price"] == 1100
    assert data["booking_ref"].startswith("CAP-")

def test_client_cannot_control_price(client):
    response = client.post("/api/bookings", json={
        "passenger_name": "Test User",
        "email": "test@example.com",
        "route": "Delhi - Chandigarh",
        "travel_date": "2026-12-01",
        "seats": 2,
        "price_per_seat": 1,
        "total_price": 2
    })
    assert response.status_code == 201
    assert response.get_json()["total_price"] == 900

def test_invalid_route_is_rejected(client):
    response = client.post("/api/bookings", json={
        "passenger_name": "Test User",
        "email": "test@example.com",
        "route": "Fake Route",
        "travel_date": "2026-12-01",
        "seats": 1
    })
    assert response.status_code == 400

def test_booking_lookup(client):
    create = client.post("/api/bookings", json={
        "passenger_name": "Lookup User",
        "email": "lookup@example.com",
        "route": "Delhi - Amritsar",
        "travel_date": "2026-12-01",
        "seats": 1
    }).get_json()
    lookup = client.get("/api/bookings/" + create["booking_ref"])
    assert lookup.status_code == 200
    assert lookup.get_json()["passenger_name"] == "Lookup User"
