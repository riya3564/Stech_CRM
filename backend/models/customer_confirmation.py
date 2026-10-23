from datetime import datetime, timezone

from extensions import db


class CustomerConfirmation(db.Model):
    __tablename__ = "customer_confirmations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    confirmation_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    service_call_id = db.Column(
        db.Integer,
        db.ForeignKey("service_calls.id"),
        nullable=False,
        index=True
    )

    repair_id = db.Column(
        db.Integer,
        db.ForeignKey("repairs.id"),
        nullable=False,
        index=True
    )

    testing_id = db.Column(
        db.Integer,
        db.ForeignKey("testings.id"),
        nullable=False,
        index=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING",
        index=True
    )

    confirmation_mode = db.Column(
        db.String(30),
        nullable=True
    )

    happy_code = db.Column(
        db.String(20),
        nullable=True
    )

    customer_remarks = db.Column(
        db.Text,
        nullable=True
    )

    confirmed_at = db.Column(
        db.DateTime(timezone=True),
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

    service_call = db.relationship(
        "ServiceCall",
        backref=db.backref(
            "customer_confirmations",
            lazy=True
        )
    )

    repair = db.relationship(
        "Repair",
        backref=db.backref(
            "customer_confirmations",
            lazy=True
        )
    )

    testing = db.relationship(
        "Testing",
        backref=db.backref(
            "customer_confirmations",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<CustomerConfirmation {self.confirmation_code}>"
