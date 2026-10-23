from datetime import datetime, timezone

from extensions import db


class ProductModel(db.Model):
    __tablename__ = "product_models"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    model_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    model_number = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    model_name = db.Column(
        db.String(150),
        nullable=True
    )

    brand_id = db.Column(
        db.Integer,
        db.ForeignKey("brands.id"),
        nullable=False,
        index=True
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
        nullable=False,
        index=True
    )

    description = db.Column(
        db.String(500),
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

    brand = db.relationship(
        "Brand",
        backref=db.backref(
            "product_models",
            lazy=True
        )
    )

    category = db.relationship(
        "ProductCategory",
        backref=db.backref(
            "product_models",
            lazy=True
        )
    )

    product_type = db.relationship(
        "ProductType",
        backref=db.backref(
            "product_models",
            lazy=True
        )
    )