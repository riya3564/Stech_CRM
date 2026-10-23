from datetime import datetime, timezone

from extensions import db


class ASCAssignment(db.Model):
    __tablename__ = "asc_assignments"

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

    assignment_status = db.Column(
        db.String(30),
        nullable=False,
        default="Assigned",
        index=True
    )

    assigned_at = db.Column(
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