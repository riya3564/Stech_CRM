from datetime import datetime, timedelta, date, time, timezone
from sqlalchemy import MetaData, select, update, insert, func
from app import app
from extensions import db
import random

# ============================================================
# STech CRM - DATA REPAIR + TEST DATA SEEDER
# Preserves existing primary keys and does not drop tables.
# All generated personal/contact data is fictional.
# ============================================================

random.seed(2026)
NOW = datetime.now(timezone.utc)

CITIES = [
    ("Haldwani", "Uttarakhand", "263139"),
    ("Dehradun", "Uttarakhand", "248001"),
    ("Rudrapur", "Uttarakhand", "263153"),
    ("Delhi", "Delhi", "110001"),
    ("Noida", "Uttar Pradesh", "201301"),
    ("Gurugram", "Haryana", "122001"),
    ("Ghaziabad", "Uttar Pradesh", "201001"),
    ("Bareilly", "Uttar Pradesh", "243001"),
    ("Moradabad", "Uttar Pradesh", "244001"),
    ("Haridwar", "Uttarakhand", "249401"),
]

FIRST = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan",
    "Rahul", "Amit", "Ankit", "Karan", "Mohit",
    "Priya", "Ananya", "Neha", "Pooja", "Riya",
    "Sneha", "Kavita", "Simran", "Aditi", "Isha",
    "Deepak", "Manish", "Nitin", "Varun", "Saurabh",
    "Shreya", "Nisha", "Megha", "Sakshi", "Divya",
]

LAST = [
    "Sharma", "Verma", "Joshi", "Pandey", "Singh",
    "Gupta", "Mishra", "Rawat", "Negi", "Pant",
    "Kumar", "Agarwal", "Bisht", "Chauhan", "Mehta",
]

COMPLAINTS = [
    "Product does not switch on despite a working power supply.",
    "Cooling performance is lower than expected.",
    "Unusual operating noise reported by the customer.",
    "Water leakage reported during normal operation.",
    "Display flashes and the controls respond intermittently.",
    "Remote control operation is inconsistent.",
    "Product stops working after running for some time.",
    "Customer has requested an installation visit.",
    "Intermittent operating fault reported.",
    "Preventive service and product inspection requested.",
    "Heating performance is below the expected level.",
    "Water remains inside the appliance after the cycle.",
    "Error indication displayed during operation.",
    "Technical diagnosis is required before repair.",
    "Customer requests an engineer inspection.",
]

STATUSES = [
    "Open", "Registered", "Validated", "Assigned",
    "Appointment Scheduled", "In Progress", "Part Required",
    "Part Pending", "Repair In Progress", "Repair Completed",
    "Testing", "Customer Confirmation", "Revisit", "Closed",
]

ASSIGNED = {
    "Assigned", "Appointment Scheduled", "In Progress",
    "Part Required", "Part Pending", "Repair In Progress",
    "Repair Completed", "Testing", "Customer Confirmation",
    "Revisit", "Closed",
}

APPOINTMENT_STATUS = {
    "Appointment Scheduled": "Scheduled",
    "In Progress": "In Progress",
    "Part Required": "Completed",
    "Part Pending": "Completed",
    "Repair In Progress": "In Progress",
    "Repair Completed": "Completed",
    "Testing": "Completed",
    "Customer Confirmation": "Completed",
    "Revisit": "Scheduled",
    "Closed": "Completed",
}


def main():
    md = MetaData()
    md.reflect(bind=db.engine)

    def tbl(name):
        return md.tables.get(name)

    def all_rows(name):
        t = tbl(name)
        if t is None:
            return []
        return [
            dict(r)
            for r in db.session.execute(select(t)).mappings().all()
        ]

    def get_by(name, column, value):
        t = tbl(name)
        if t is None or column not in t.c:
            return None
        result = db.session.execute(
            select(t).where(t.c[column] == value).limit(1)
        ).mappings().first()
        return dict(result) if result else None

    def save_new(name, key, value, values):
        """Insert when absent; return existing row when present."""
        t = tbl(name)
        if t is None:
            raise RuntimeError(f"Required table missing: {name}")

        existing = get_by(name, key, value)
        if existing:
            return existing

        data = dict(values)
        data[key] = value

        for col in t.columns:
            if col.name in ("created_at", "updated_at"):
                data.setdefault(col.name, NOW)

        data = {k: v for k, v in data.items() if k in t.c}

        result = db.session.execute(
            insert(t).values(**data).returning(t)
        ).mappings().first()

        return dict(result)

    def patch(name, row_id, values):
        """Update only columns that actually exist in the schema."""
        t = tbl(name)
        if t is None or "id" not in t.c:
            return

        data = {k: v for k, v in values.items() if k in t.c}
        if "updated_at" in t.c:
            data["updated_at"] = NOW

        if data:
            db.session.execute(
                update(t).where(t.c.id == row_id).values(**data)
            )

    def ensure_relation(name, match, values):
        """Create a relation only when its matching row is absent."""
        t = tbl(name)
        if t is None:
            print(f"Optional table missing: {name}")
            return

        for k in match:
            if k not in t.c:
                raise RuntimeError(f"{name} has no column {k}")

        conditions = [t.c[k] == v for k, v in match.items()]
        existing = db.session.execute(
            select(t).where(*conditions).limit(1)
        ).mappings().first()

        data = dict(values)
        data.update(match)

        if existing:
            patch(name, existing["id"], data)
            return

        for col in t.columns:
            if col.name in ("created_at", "updated_at"):
                data.setdefault(col.name, NOW)

        data = {k: v for k, v in data.items() if k in t.c}
        db.session.execute(insert(t).values(**data))

    # Validate master records first.
    models = all_rows("product_models")
    call_types = all_rows("call_types")
    symptoms = all_rows("symptom_codes")

    if not models or not call_types or not symptoms:
        raise RuntimeError(
            "Missing product_models, call_types or symptom_codes. "
            "No changes have been committed."
        )

    # Reuse previously created demo records when available.
    asc_ids = []
    for i in range(1, 11):
        city, state, pin = CITIES[i - 1]
        code = f"IND-ASC-{i:03d}"

        rec = save_new("asc", "asc_code", code, {
            "asc_code": code,
            "asc_name": f"STech {city} Service Centre {i:02d}",
            "contact_person": f"{FIRST[(i-1) % len(FIRST)]} "
                              f"{LAST[(i-1) % len(LAST)]}",
            "phone": f"900000{i:04d}",
            "email": f"servicecentre{i:03d}@example.com",
            "address": f"Service Road, Sector {i}, {city}",
            "city": city, "state": state, "pin_code": pin,
            "status": "Active",
        })
        asc_ids.append(rec["id"])

    engineer_ids = []
    for i in range(1, 31):
        city, state, pin = CITIES[(i - 1) % len(CITIES)]
        code = f"IND-ENG-{i:03d}"

        rec = save_new("engineers", "engineer_code", code, {
            "engineer_code": code,
            "engineer_name": (
                f"{FIRST[(i + 7) % len(FIRST)]} "
                f"{LAST[(i + 3) % len(LAST)]}"
            ),
            "asc_id": asc_ids[(i - 1) % len(asc_ids)],
            "phone": f"910000{i:04d}",
            "email": f"engineer{i:03d}@example.com",
            "specialization": [
                "Installation", "Cooling Appliances",
                "Home Appliances", "Electronics Repair",
                "General Service",
            ][(i - 1) % 5],
            "status": "Active",
            "city": city, "district": city, "state": state,
            "pin_code": pin, "service_area": city,
            "joining_date": date.today() - timedelta(days=120 + i),
        })
        # Also repair details on previously seeded engineer records.
        patch("engineers", rec["id"], {
            "asc_id": asc_ids[(i - 1) % len(asc_ids)],
            "status": "Active",
        })
        engineer_ids.append(rec["id"])

    customer_ids = []
    for i in range(1, 101):
        city, state, pin = CITIES[(i - 1) % len(CITIES)]
        name = (
            f"{FIRST[(i - 1) % len(FIRST)]} "
            f"{LAST[((i - 1) // len(FIRST)) % len(LAST)]}"
        )
        code = f"IND-CUST-{i:04d}"

        rec = save_new("customers", "customer_code", code, {
            "customer_code": code,
            "full_name": name,
            "mobile": f"920000{i:04d}",
            "email": f"customer{i:04d}@example.com",
            "customer_type": "Individual",
            "address_line": f"House {100+i}, Main Road, {city}",
            "city": city, "state": state, "pin_code": pin,
            "status": "Active",
        })
        patch("customers", rec["id"], {
            "full_name": name,
            "city": city,
            "state": state,
            "pin_code": pin,
            "status": "Active",
        })
        customer_ids.append(rec["id"])

    cp_ids = []
    if tbl("customer_products") is not None:
        for i in range(1, 101):
            model = models[(i - 1) % len(models)]
            code = f"IND-CP-{i:04d}"
            serial = f"STX26{i:08d}"

            rec = save_new(
                "customer_products", "customer_product_code", code, {
                    "customer_product_code": code,
                    "customer_id": customer_ids[i - 1],
                    "product_model_id": model["id"],
                    "serial_number": serial,
                    "purchase_date": date.today() - timedelta(days=220+i),
                    "installation_date": date.today() - timedelta(days=215+i),
                    "warranty_start_date": date.today() - timedelta(days=220+i),
                    "warranty_end_date": date.today() + timedelta(days=145),
                    "status": "Active",
                }
            )
            patch("customer_products", rec["id"], {
                "customer_id": customer_ids[i - 1],
                "product_model_id": model["id"],
                "serial_number": serial,
                "status": "Active",
            })
            cp_ids.append(rec["id"])

    # Update existing DUMMY service calls IN PLACE first.
    # This preserves their primary keys and existing related records.
    calls = tbl("service_calls")
    dummy_calls = db.session.execute(
        select(calls)
        .where(calls.c.call_id.like("DUMMY-CALL-%"))
        .order_by(calls.c.id)
    ).mappings().all()

    for index, old in enumerate(dummy_calls, start=1):
        customer_index = (index - 1) % len(customer_ids)
        model = models[(index - 1) % len(models)]
        call_type = call_types[(index - 1) % len(call_types)]
        symptom = symptoms[(index - 1) % len(symptoms)]
        city, state, pin = CITIES[(index - 1) % len(CITIES)]

        status = old["status"]
        assigned = status in ASSIGNED
        engineer_id = (
            engineer_ids[(index - 1) % len(engineer_ids)]
            if assigned else None
        )

        registered = old.get("registered_at") or (
            NOW - timedelta(days=index % 20)
        )

        values = {
            "call_id": f"IND-CALL-{index:05d}",
            "complaint_id": f"IND-COMP-{index:05d}",
            "customer_id": customer_ids[customer_index],
            "product_model_id": model["id"],
            "call_type_id": call_type["id"],
            "symptom_id": symptom["id"],
            "serial_number": f"STX26{customer_index+1:08d}",
            "complaint_description": random.choice(COMPLAINTS),
            "service_address": (
                f"House {100+customer_index}, Main Road, {city}"
            ),
            "city": city, "state": state, "pin_code": pin,
            "priority": ["Normal", "High", "Low"][index % 3],
            "serviceability_status": "Serviceable",
            "duplicate_check_status": "Clear",
            "registered_at": registered,
            "sla_start_at": registered,
            "sla_due_at": registered + timedelta(hours=48),
            "engineer_id": engineer_id,
            "engineer_assignment_remarks": (
                "Assigned for service fulfilment" if assigned else None
            ),
            "engineer_assigned_at": registered if assigned else None,
        }

        if cp_ids and "customer_product_id" in calls.c:
            values["customer_product_id"] = cp_ids[customer_index]

        # Do not rename to a code that already belongs to another row.
        new_call_code = f"IND-CALL-{index:05d}"
        conflict = db.session.execute(
            select(calls.c.id).where(
                calls.c.call_id == new_call_code,
                calls.c.id != old["id"],
            ).limit(1)
        ).first()

        if conflict:
            values["call_id"] = f"REPAIRED-CALL-{old['id']:06d}"
            values["complaint_id"] = f"REPAIRED-COMP-{old['id']:06d}"

        patch("service_calls", old["id"], values)

        if assigned:
            asc_id = asc_ids[(index - 1) % len(asc_ids)]
            ensure_relation(
                "asc_assignments",
                {"service_call_id": old["id"]},
                {
                    "asc_id": asc_id,
                    "assignment_status": "Assigned",
                    "assigned_at": registered,
                    "remarks": "Assigned for service fulfilment",
                },
            )

            if tbl("appointments") is not None:
                engineer = get_by("engineers", "id", engineer_id)
                ensure_relation(
                    "appointments",
                    {"service_call_id": old["id"]},
                    {
                        "asc_id": engineer["asc_id"],
                        "engineer_id": engineer_id,
                        "appointment_date": date.today() + timedelta(days=1),
                        "appointment_time": time(10 + index % 7, 0),
                        "appointment_point": "Customer Address",
                        "status": APPOINTMENT_STATUS.get(status, "Scheduled"),
                        "remarks": "Customer service visit",
                        "scheduled_at": NOW,
                    },
                )

    # Create missing IND calls without duplicating existing call IDs.
    for i in range(1, 501):
        call_code = f"IND-CALL-{i:05d}"
        if get_by("service_calls", "call_id", call_code):
            continue

        customer_index = (i - 1) % len(customer_ids)
        model = models[(i - 1) % len(models)]
        call_type = call_types[(i - 1) % len(call_types)]
        symptom = symptoms[(i - 1) % len(symptoms)]
        city, state, pin = CITIES[(i - 1) % len(CITIES)]
        status = STATUSES[(i - 1) % len(STATUSES)]
        registered = NOW - timedelta(days=i % 30, hours=i % 12)
        engineer_id = (
            engineer_ids[(i - 1) % len(engineer_ids)]
            if status in ASSIGNED else None
        )

        values = {
            "call_id": call_code,
            "complaint_id": f"IND-COMP-{i:05d}",
            "customer_id": customer_ids[customer_index],
            "product_model_id": model["id"],
            "customer_product_id": (
                cp_ids[customer_index] if cp_ids else None
            ),
            "call_type_id": call_type["id"],
            "symptom_id": symptom["id"],
            "serial_number": f"STX26{customer_index+1:08d}",
            "complaint_description": random.choice(COMPLAINTS),
            "service_address": f"House {100+customer_index}, Main Road, {city}",
            "city": city, "state": state, "pin_code": pin,
            "priority": ["Normal", "High", "Low"][i % 3],
            "status": status,
            "serviceability_status": "Serviceable",
            "duplicate_check_status": "Clear",
            "registered_at": registered,
            "sla_start_at": registered,
            "sla_due_at": registered + timedelta(hours=48),
            "engineer_id": engineer_id,
            "engineer_assignment_remarks": (
                "Assigned for service fulfilment" if engineer_id else None
            ),
            "engineer_assigned_at": registered if engineer_id else None,
        }

        rec = save_new("service_calls", "call_id", call_code, values)

        if engineer_id:
            engineer = get_by("engineers", "id", engineer_id)
            ensure_relation(
                "asc_assignments",
                {"service_call_id": rec["id"]},
                {
                    "asc_id": engineer["asc_id"],
                    "assignment_status": "Assigned",
                    "assigned_at": registered,
                    "remarks": "Assigned for service fulfilment",
                },
            )
            if tbl("appointments") is not None:
                ensure_relation(
                    "appointments",
                    {"service_call_id": rec["id"]},
                    {
                        "asc_id": engineer["asc_id"],
                        "engineer_id": engineer_id,
                        "appointment_date": date.today() + timedelta(days=1),
                        "appointment_time": time(10 + i % 7, 0),
                        "appointment_point": "Customer Address",
                        "status": APPOINTMENT_STATUS.get(status, "Scheduled"),
                        "remarks": "Customer service visit",
                        "scheduled_at": NOW,
                    },
                )

    db.session.commit()

    print("\n========== SEED COMPLETED ==========")
    for name in (
        "customers", "customer_products", "asc", "engineers",
        "service_calls", "asc_assignments", "appointments",
    ):
        if tbl(name) is not None:
            print(f"{name}: {db.session.execute(select(func.count()).select_from(tbl(name))).scalar_one()}")

    print("\nSample calls:")
    for r in db.session.execute(
        select(calls.c.call_id, calls.c.complaint_id, calls.c.status)
        .order_by(calls.c.id.desc()).limit(10)
    ):
        print(r)

    print("\nFictional test data only. No tables were dropped.")


with app.app_context():
    try:
        main()
    except Exception as exc:
        db.session.rollback()
        print(f"\nSEED FAILED; transaction rolled back: {exc}")
        raise
