from datetime import datetime, timezone

from extensions import db


class EngineerVisit(db.Model):
    __tablename__ = "engineer_visits"

    id = db.Column(db.Integer, primary_key=True)

    visit_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True
    )

    service_call_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    appointment_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    engineer_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    visit_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    arrival_time = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    departure_time = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    customer_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    observations = db.Column(
        db.Text,
        nullable=True
    )

    initial_observation = db.Column(
        db.Text,
        nullable=True
    )

    part_required = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    outcome = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(40),
        nullable=False,
        default="Scheduled",
        index=True
    )

    revisit_required = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    remarks = db.Column(
        db.String(500),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )