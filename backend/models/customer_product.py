from datetime import date, datetime, timezone

from extensions import db


class CustomerProduct(db.Model):
    __tablename__ = "customer_products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_product_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    product_model_id = db.Column(
        db.Integer,
        db.ForeignKey("product_models.id"),
        nullable=False,
        index=True
    )

    serial_number = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    purchase_date = db.Column(
        db.Date,
        nullable=True
    )

    installation_date = db.Column(
        db.Date,
        nullable=True
    )

    warranty_start_date = db.Column(
        db.Date,
        nullable=True
    )

    warranty_end_date = db.Column(
        db.Date,
        nullable=True
    )

    amc_start_date = db.Column(
        db.Date,
        nullable=True
    )

    amc_end_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active",
        index=True
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

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "customer_products",
            lazy=True
        )
    )

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref(
            "customer_products",
            lazy=True
        )
    )