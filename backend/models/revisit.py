from datetime import datetime, timezone

from extensions import db


class Revisit(db.Model):
    __tablename__ = "revisits"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    revisit_code = db.Column(
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

    previous_service_call_id = db.Column(
        db.Integer,
        db.ForeignKey("service_calls.id"),
        nullable=True,
        index=True
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="OPEN",
        index=True
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Normal"
    )

    remarks = db.Column(
        db.Text,
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
        foreign_keys=[service_call_id],
        backref=db.backref(
            "revisits",
            lazy=True
        )
    )

    previous_service_call = db.relationship(
        "ServiceCall",
        foreign_keys=[previous_service_call_id]
    )

    def __repr__(self):
        return f"<Revisit {self.revisit_code}>"
