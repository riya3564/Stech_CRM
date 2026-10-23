from datetime import datetime, timezone

from extensions import db


class Diagnosis(db.Model):
    __tablename__ = "diagnoses"

    id = db.Column(db.Integer, primary_key=True)

    diagnosis_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True
    )

    service_call_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    visit_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    symptom_code_id = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    fault_code_id = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    diagnosis_code_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    observation = db.Column(
        db.Text,
        nullable=True
    )

    actual_fault = db.Column(
        db.Text,
        nullable=True
    )

    root_cause = db.Column(
        db.Text,
        nullable=True
    )

    diagnostic_actions = db.Column(
        db.Text,
        nullable=True
    )

    customer_issue = db.Column(
        db.Text,
        nullable=True
    )

    product_issue = db.Column(
        db.Text,
        nullable=True
    )

    part_required = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    evidence = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Diagnosed",
        index=True
    )

    remarks = db.Column(
        db.String(500),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )