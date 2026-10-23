from datetime import datetime

from extensions import db


class Testing(db.Model):
    __tablename__ = "testings"

    id = db.Column(db.Integer, primary_key=True)

    # Testing reference
    testing_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    # Repair against which testing is performed
    repair_id = db.Column(
        db.Integer,
        db.ForeignKey("repairs.id"),
        nullable=False
    )

    # Testing result
    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING"
    )

    # Engineer / technician observations
    remarks = db.Column(db.Text, nullable=True)

    # Who performed testing
    tested_by = db.Column(
        db.Integer,
        db.ForeignKey("engineers.id"),
        nullable=True
    )

    tested_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    repair = db.relationship(
        "Repair",
        backref=db.backref(
            "testing_records",
            lazy=True
        )
    )

    engineer = db.relationship(
        "Engineer",
        backref=db.backref(
            "testing_records",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Testing {self.testing_code}>"