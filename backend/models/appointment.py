from datetime import datetime, timezone

from extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    service_call_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    asc_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    engineer_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    appointment_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    appointment_time = db.Column(
        db.String(20),
        nullable=True
    )

    appointment_point = db.Column(
        db.String(300),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Scheduled",
        index=True
    )

    remarks = db.Column(
        db.String(500),
        nullable=True
    )

    scheduled_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
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