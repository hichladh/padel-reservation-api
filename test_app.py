import pytest

from app import app, db, Court, Reservation


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_create_court(client):
    response = client.post(
        "/courts",
        json={"name": "Court 1"},
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Court 1"


def test_create_reservation(client):
    client.post(
        "/courts",
        json={"name": "Court 1"},
    )

    response = client.post(
        "/reservations",
        json={
            "customer_name": "Hichem",
            "court_id": 1,
            "start_time": "2026-10-01T18:00:00",
            "end_time": "2026-10-01T19:30:00",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["customer_name"] == "Hichem"


def test_overlapping_reservation_is_rejected(client):
    client.post(
        "/courts",
        json={"name": "Court 1"},
    )

    reservation = {
        "customer_name": "Hichem",
        "court_id": 1,
        "start_time": "2026-10-01T18:00:00",
        "end_time": "2026-10-01T19:30:00",
    }

    client.post("/reservations", json=reservation)

    conflicting_reservation = {
        "customer_name": "Peter",
        "court_id": 1,
        "start_time": "2026-10-01T19:00:00",
        "end_time": "2026-10-01T20:00:00",
    }

    response = client.post(
        "/reservations",
        json=conflicting_reservation,
    )

    assert response.status_code == 409