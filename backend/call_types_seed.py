from app import app
from extensions import db
from models.call_type import CallType


CALL_TYPES = [
    {
        "code": "INSTALLATION",
        "name": "Installation",
        "description": "New product installation service request"
    },
    {
        "code": "REPAIR",
        "name": "Repair",
        "description": "Product repair service request"
    },
    {
        "code": "BREAKDOWN",
        "name": "Breakdown",
        "description": "Product has stopped working or has a major operational failure"
    },
    {
        "code": "PREVENTIVE_MAINTENANCE",
        "name": "Preventive Maintenance",
        "description": "Scheduled preventive maintenance service"
    },
    {
        "code": "DEMO",
        "name": "Demo",
        "description": "Product demonstration request"
    },
    {
        "code": "INSPECTION",
        "name": "Inspection",
        "description": "Product inspection or assessment request"
    },
    {
        "code": "REVISIT",
        "name": "Revisit",
        "description": "Follow-up visit for an existing service case"
    },
    {
        "code": "REPEAT_COMPLAINT",
        "name": "Repeat Complaint",
        "description": "Complaint repeated after previous service"
    },
    {
        "code": "OTHER",
        "name": "Other",
        "description": "Other service-related request"
    }
]


with app.app_context():
    for item in CALL_TYPES:
        existing = db.session.scalar(
            db.select(CallType).where(
                CallType.call_type_code == item["code"]
            )
        )

        if not existing:
            db.session.add(
                CallType(
                    call_type_code=item["code"],
                    call_type_name=item["name"],
                    description=item["description"],
                    status="Active"
                )
            )

    db.session.commit()

    print("Call types seeded successfully.")