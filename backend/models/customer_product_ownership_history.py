from datetime import datetime, timezone

from extensions import db


class CustomerProductOwnershipHistory(db.Model):
    __tablename__ = "customer_product_ownership_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_product_id = db.Column(
        db.Integer,
        db.ForeignKey("customer_products.id"),
        nullable=False,
        index=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    valid_from = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    valid_to = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    change_reason = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    customer_product = db.relationship(
        "CustomerProduct",
        backref=db.backref(
            "ownership_history",
            lazy=True
        )
    )

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "ownership_history",
            lazy=True
        )
    )