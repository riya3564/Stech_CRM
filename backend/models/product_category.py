from datetime import datetime, timezone

from extensions import db


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    category_name = db.Column(
        db.String(100),
        unique=True,
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