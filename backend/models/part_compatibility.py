from datetime import datetime, timezone
from extensions import db


class PartCompatibility(db.Model):
    __tablename__ = "part_compatibility"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    product_model_id = db.Column(
        db.Integer,
        db.ForeignKey("product_models.id"),
        nullable=True,
        index=True
    )

    diagnosis_id = db.Column(
        db.Integer,
        db.ForeignKey("diagnosis_codes.id"),
        nullable=False,
        index=True
    )

    repair_id = db.Column(
        db.Integer,
        db.ForeignKey("repair_codes.id"),
        nullable=False,
        index=True
    )

    part_id = db.Column(
        db.Integer,
        db.ForeignKey("parts.id"),
        nullable=False,
        index=True
    )

    priority = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    notes = db.Column(
        db.String(500),
        nullable=True
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

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref(
            "part_compatibilities",
            lazy=True
        )
    )

    diagnosis = db.relationship(
        "DiagnosisCode",
        backref=db.backref(
            "part_compatibilities",
            lazy=True
        )
    )

    repair = db.relationship(
        "RepairCode",
        backref=db.backref(
            "part_compatibilities",
            lazy=True
        )
    )

    part = db.relationship(
        "Part",
        backref=db.backref(
            "compatibilities",
            lazy=True
        )
    )