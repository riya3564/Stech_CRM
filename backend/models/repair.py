from datetime import datetime, timezone

from extensions import db


class Repair(db.Model):
    __tablename__ = "repairs"

    id = db.Column(db.Integer, primary_key=True)

    repair_number = db.Column(
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

    repair_code_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    part_required = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    actual_repair_action = db.Column(
        db.Text,
        nullable=True
    )

    repair_result = db.Column(
        db.Text,
        nullable=True
    )

    skill_required = db.Column(
        db.String(200),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending",
        index=True
    )

    testing_required = db.Column(
        db.Boolean,
        nullable=False,
        default=True
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