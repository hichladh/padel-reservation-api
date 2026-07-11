from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class Court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(100),
        nullable=False,
    )

    court_id = db.Column(
        db.Integer,
        db.ForeignKey("court.id"),
        nullable=False,
    )

    start_time = db.Column(
        db.DateTime,
        nullable=False,
    )

    end_time = db.Column(
        db.DateTime,
        nullable=False,
    )

    court = db.relationship("Court")

@app.get("/health")
def health():
    return jsonify(status="UP"), 200


@app.get("/courts")
def get_courts():
    courts = Court.query.all()

    result = []

    for court in courts:
        result.append(
            {
                "id": court.id,
                "name": court.name,
            }
        )

    return jsonify(result), 200

@app.get("/reservations")
def get_reservations():
    reservations = Reservation.query.all()

    result = []

    for reservation in reservations:
        result.append(
            {
                "id": reservation.id,
                "customer_name": reservation.customer_name,
                "court_id": reservation.court_id,
                "court_name": reservation.court.name,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
            }
        )

    return jsonify(result), 200


@app.post("/courts")
def create_court():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify(error="Court name is required"), 400

    existing_court = Court.query.filter_by(name=data["name"]).first()

    if existing_court:
        return jsonify(error="Court already exists"), 409

    court = Court(name=data["name"])

    db.session.add(court)
    db.session.commit()

    return jsonify(
        id=court.id,
        name=court.name,
    ), 201


@app.post("/reservations")
def create_reservation():
    data = request.get_json()

    required_fields = [
        "customer_name",
        "court_id",
        "start_time",
        "end_time",
    ]

    if not data or any(
        not data.get(field) for field in required_fields
    ):
        return jsonify(
            error="Missing required reservation data"
        ), 400

    court = db.session.get(Court, data["court_id"])

    if court is None:
        return jsonify(error="Court not found"), 404

    try:
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"])
    except ValueError:
        return jsonify(error="Invalid date format"), 400

    if start_time >= end_time:
        return jsonify(
            error="End time must be after start time"
        ), 400

    conflicting_reservation = Reservation.query.filter(
        Reservation.court_id == data["court_id"],
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    ).first()

    if conflicting_reservation:
        return jsonify(
            error="Court is already reserved during this time"
        ), 409

    reservation = Reservation(
        customer_name=data["customer_name"],
        court_id=data["court_id"],
        start_time=start_time,
        end_time=end_time,
    )

    db.session.add(reservation)
    db.session.commit()

    return jsonify(
        id=reservation.id,
        customer_name=reservation.customer_name,
        court_id=reservation.court_id,
        court_name=court.name,
        start_time=reservation.start_time.isoformat(),
        end_time=reservation.end_time.isoformat(),
    ), 201

@app.delete("/reservations/<int:reservation_id>")
def delete_reservation(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)

    if reservation is None:
        return jsonify(error="Reservation not found"), 404

    db.session.delete(reservation)
    db.session.commit()

    return jsonify(message="Reservation cancelled successfully"), 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)