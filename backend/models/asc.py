from datetime import datetime, timezone

from extensions import db


class ASC(db.Model):
    __tablename__ = "asc"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    asc_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True
    )

    asc_name = db.Column(
        db.String(150),
        nullable=False
    )

    contact_person = db.Column(
        db.String(150),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    address = db.Column(
        db.String(300),
        nullable=True
    )

    city = db.Column(
        db.String(100),
        nullable=True
    )

    state = db.Column(
        db.String(100),
        nullable=True
    )

    pin_code = db.Column(
        db.String(10),
        nullable=False,
        index=True
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