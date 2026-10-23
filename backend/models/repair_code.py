from datetime import datetime, timezone

from extensions import db


class RepairCode(db.Model):
    __tablename__ = "repair_codes"

    id = db.Column(db.Integer, primary_key=True)

    repair_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    repair_name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.id"),
        nullable=False,
        index=True
    )

    product_type_id = db.Column(
        db.Integer,
        db.ForeignKey("product_types.id"),
        nullable=True,
        index=True
    )

    product_model_id = db.Column(
        db.Integer,
        db.ForeignKey("product_models.id"),
        nullable=True,
        index=True
    )

    fault_id = db.Column(
        db.Integer,
        db.ForeignKey("fault_codes.id"),
        nullable=False,
        index=True
    )

    diagnosis_id = db.Column(
        db.Integer,
        db.ForeignKey("diagnosis_codes.id"),
        nullable=False,
        index=True
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

    category = db.relationship(
        "ProductCategory",
        backref=db.backref("repair_codes", lazy=True)
    )

    product_type = db.relationship(
        "ProductType",
        backref=db.backref("repair_codes", lazy=True)
    )

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref("repair_codes", lazy=True)
    )

    fault = db.relationship(
        "FaultCode",
        backref=db.backref("repair_codes", lazy=True)
    )

    diagnosis = db.relationship(
        "DiagnosisCode",
        backref=db.backref("repair_codes", lazy=True)
    )