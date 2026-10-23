
from datetime import datetime, timezone

from extensions import db


class Engineer(db.Model):
    __tablename__ = "engineers"

    id = db.Column(db.Integer, primary_key=True)

    engineer_code = db.Column(
        db.String(50), nullable=False, unique=True, index=True
    )
    engineer_name = db.Column(db.String(150), nullable=False)
    asc_id = db.Column(db.Integer, nullable=False, index=True)

    phone = db.Column(db.String(20), nullable=True)
    alternate_phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(150), nullable=True)

    # Aadhaar is sensitive personal information.
    # Never include this field in list/detail API responses.
    aadhaar_number = db.Column(db.String(12), nullable=True)

    address = db.Column(db.String(250), nullable=True)
    landmark = db.Column(db.String(150), nullable=True)
    locality = db.Column(db.String(150), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pin_code = db.Column(db.String(10), nullable=True)

    specialization = db.Column(db.String(200), nullable=True)
    service_area = db.Column(db.String(200), nullable=True)
    joining_date = db.Column(db.Date, nullable=True)

    status = db.Column(
        db.String(20), nullable=False, default="Active", index=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
