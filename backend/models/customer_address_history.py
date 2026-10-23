from datetime import datetime, timezone

from extensions import db


class CustomerAddressHistory(db.Model):
    __tablename__ = "customer_address_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
        index=True
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

    valid_from = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    valid_to = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    change_reason = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "address_history",
            lazy=True
        )
    )