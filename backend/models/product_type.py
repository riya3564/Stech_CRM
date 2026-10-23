from datetime import datetime, timezone

from extensions import db


class ProductType(db.Model):
    __tablename__ = "product_types"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    type_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    type_name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.id"),
        nullable=False,
        index=True
    )

    description = db.Column(
        db.String(255),
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

    category = db.relationship(
        "ProductCategory",
        backref=db.backref(
            "product_types",
            lazy=True
        )
    )