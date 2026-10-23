from datetime import datetime, timezone

from extensions import db


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    part_id = db.Column(
        db.Integer,
        db.ForeignKey("parts.id"),
        nullable=False,
        unique=True,
        index=True
    )

    warehouse_name = db.Column(
        db.String(150),
        nullable=True
    )

    available_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    reserved_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    reorder_level = db.Column(
        db.Integer,
        nullable=False,
        default=0
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

    part = db.relationship(
        "Part",
        backref=db.backref(
            "inventory",
            uselist=False
        )
    )