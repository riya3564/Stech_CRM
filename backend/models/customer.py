from datetime import datetime, timezone

from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)

    customer_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    mobile = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    customer_type = db.Column(
        db.String(30),
        nullable=False,
        default="Individual"
    )

    address_line = db.Column(
        db.String(255),
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
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )