from datetime import datetime, timezone

from extensions import db


class SymptomCode(db.Model):
    __tablename__ = "symptom_codes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    symptom_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    symptom_name = db.Column(
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
        backref=db.backref(
            "symptom_codes",
            lazy=True
        )
    )

    product_type = db.relationship(
        "ProductType",
        backref=db.backref(
            "symptom_codes",
            lazy=True
        )
    )

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref(
            "symptom_codes",
            lazy=True
        )
    )