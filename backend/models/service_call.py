from datetime import datetime, timezone

from extensions import db


class ServiceCall(db.Model):
    __tablename__ = "service_calls"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Internal / legacy call number
    call_id = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # Customer-facing Complaint ID
    # Example:
    # UK04-SONY-PRD-20261008-000007-R
    complaint_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True,
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

    customer_product_id = db.Column(
        db.Integer,
        db.ForeignKey("customer_products.id"),
        nullable=True,
        index=True
    )

    call_type_id = db.Column(
        db.Integer,
        db.ForeignKey("call_types.id"),
        nullable=False,
        index=True
    )

    symptom_id = db.Column(
        db.Integer,
        db.ForeignKey("symptom_codes.id"),
        nullable=False,
        index=True
    )

    serial_number = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    complaint_description = db.Column(
        db.Text,
        nullable=False
    )

    service_address = db.Column(
        db.String(255),
        nullable=True
    )

    city = db.Column(
        db.String(100),
        nullable=True
    )

    state = db.Column(
        db.String(100),
        nullable=True
    )

    pin_code = db.Column(
        db.String(10),
        nullable=True
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Normal"
    )

    # New calls enter Open Bucket
    status = db.Column(
        db.String(30),
        nullable=False,
        default="Open",
        index=True
    )

    serviceability_status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending"
    )

    duplicate_check_status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending"
    )

    # ---------------------------------------------------------
    # ENGINEER ASSIGNMENT
    # ---------------------------------------------------------

    engineer_id = db.Column(
        db.Integer,
        db.ForeignKey("engineers.id"),
        nullable=True,
        index=True
    )

    engineer_assignment_remarks = db.Column(
        db.String(500),
        nullable=True
    )

    engineer_assigned_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    registered_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    sla_start_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    sla_due_at = db.Column(
        db.DateTime(timezone=True),
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

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------

    customer = db.relationship(
        "Customer",
        backref=db.backref(
            "service_calls",
            lazy=True
        )
    )

    product_model = db.relationship(
        "ProductModel",
        backref=db.backref(
            "service_calls",
            lazy=True
        )
    )

    customer_product = db.relationship(
        "CustomerProduct",
        backref=db.backref(
            "service_calls",
            lazy=True
        )
    )

    call_type = db.relationship(
        "CallType",
        backref=db.backref(
            "service_calls",
            lazy=True
        )
    )

    symptom = db.relationship(
        "SymptomCode",
        backref=db.backref(
            "service_calls",
            lazy=True
        )
    )

    engineer = db.relationship(
        "Engineer",
        foreign_keys=[engineer_id]
    )