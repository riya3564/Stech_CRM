from datetime import datetime, timezone
from extensions import db


class Part(db.Model):
    __tablename__ = "parts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    part_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    part_name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    brand_id = db.Column(
        db.Integer,
        db.ForeignKey("brands.id"),
        nullable=True,
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

    brand = db.relationship(
        "Brand",
        backref=db.backref("parts", lazy=True)
    )

    category = db.relationship(
        "ProductCategory",
        backref=db.backref("parts", lazy=True)
    )

    product_type = db.relationship(
        "ProductType",
        backref=db.backref("parts", lazy=True)
    )