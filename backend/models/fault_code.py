from datetime import datetime, timezone

from extensions import db


class FaultCode(db.Model):
    __tablename__ = "fault_codes"

    id = db.Column(db.Integer, primary_key=True)

    fault_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    fault_name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    # Product applicability
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

    # Fault is linked to a customer-visible symptom
    symptom_id = db.Column(
        db.Integer,
        db.ForeignKey("symptom_codes.id"),
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

    # Relationships
    category = db.relationship(
        "ProductCategory",
        backref=db.backref("fault_codes", lazy=True)
    )

    product_type = db.relationship(
        "ProductType",
        backref=db.backref("fault_codes", lazy=True)
    )

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref("fault_codes", lazy=True)
    )

    symptom = db.relationship(
        "SymptomCode",
        backref=db.backref("fault_codes", lazy=True)
    )