from datetime import datetime, timezone

from extensions import db


class Serviceability(db.Model):
    __tablename__ = "serviceability"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pin_code = db.Column(
        db.String(10),
        nullable=False,
        index=True
    )

    city = db.Column(
        db.String(100),
        nullable=True
    )

    state = db.Column(
        db.String(100),
        nullable=True
    )

    serviceable = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active",
        index=True
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