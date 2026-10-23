from datetime import datetime, timezone

from extensions import db


class PartRequirement(db.Model):
    __tablename__ = "part_requirements"

    id = db.Column(db.Integer, primary_key=True)

    requirement_number = db.Column(
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

    visit_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    diagnosis_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    repair_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    part_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    required_reason = db.Column(
        db.Text,
        nullable=True
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Normal",
        index=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending",
        index=True
    )

    availability_status = db.Column(
        db.String(30),
        nullable=False,
        default="Checking"
    )

    requested_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
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