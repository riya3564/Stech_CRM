from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.engineer_visit import EngineerVisit
from models.service_call import ServiceCall
from models.appointment import Appointment
from models.engineer import Engineer


engineer_visits_bp = Blueprint(
    "engineer_visits",
    __name__,
    url_prefix="/api/engineer-visits"
)


@engineer_visits_bp.post("")
def create_engineer_visit():
    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    appointment_id = data.get("appointment_id")
    engineer_id = data.get("engineer_id")
    visit_date = data.get("visit_date")

    if not service_call_id:
        return jsonify({"message": "service_call_id is required"}), 400

    if not appointment_id:
        return jsonify({"message": "appointment_id is required"}), 400

    if not engineer_id:
        return jsonify({"message": "engineer_id is required"}), 400

    if not visit_date:
        return jsonify({"message": "visit_date is required"}), 400

    service_call = db.session.get(ServiceCall, service_call_id)

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    appointment = db.session.get(Appointment, appointment_id)

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    engineer = db.session.get(Engineer, engineer_id)

    if not engineer:
        return jsonify({
            "message": "Engineer not found"
        }), 404

    if engineer.status != "Active":
        return jsonify({
            "message": "Engineer is not active"
        }), 400

    if appointment.service_call_id != service_call_id:
        return jsonify({
            "message": "Appointment does not belong to this service call"
        }), 400

    if appointment.engineer_id != engineer_id:
        return jsonify({
            "message": "Engineer does not match the appointment"
        }), 400

    try:
        parsed_visit_date = datetime.strptime(
            visit_date,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "message": "visit_date must be in YYYY-MM-DD format"
        }), 400

    active_visits = db.session.scalar(
        select(EngineerVisit).where(
            EngineerVisit.service_call_id == service_call_id,
            EngineerVisit.status.notin_([
                "Completed",
                "Cancelled"
            ])
        ).limit(1)
    )

    if active_visits:
        return jsonify({
            "message": "An active engineer visit already exists for this service call",
            "visit_number": active_visits.visit_number
        }), 409

    last_visit = db.session.scalar(
        select(EngineerVisit)
        .order_by(EngineerVisit.id.desc())
        .limit(1)
    )

    next_number = 1 if not last_visit else last_visit.id + 1

    visit_number = f"VISIT-{next_number:04d}"

    visit = EngineerVisit(
        visit_number=visit_number,
        service_call_id=service_call_id,
        appointment_id=appointment_id,
        engineer_id=engineer_id,
        visit_date=parsed_visit_date,
        customer_available=data.get(
            "customer_available",
            True
        ),
        observations=data.get("observations"),
        initial_observation=data.get(
            "initial_observation"
        ),
        part_required=data.get(
            "part_required",
            False
        ),
        outcome=data.get("outcome"),
        status=data.get(
            "status",
            "Scheduled"
        ),
        revisit_required=data.get(
            "revisit_required",
            False
        ),
        remarks=data.get("remarks")
    )

    db.session.add(visit)

    service_call.status = "Engineer Visit Scheduled"

    db.session.commit()

    return jsonify({
        "message": "Engineer visit created successfully",
        "visit": {
            "id": visit.id,
            "visit_number": visit.visit_number,
            "service_call_id": visit.service_call_id,
            "appointment_id": visit.appointment_id,
            "engineer_id": visit.engineer_id,
            "visit_date": visit.visit_date.isoformat(),
            "customer_available": visit.customer_available,
            "part_required": visit.part_required,
            "status": visit.status,
            "revisit_required": visit.revisit_required,
            "observations": visit.observations,
            "initial_observation": visit.initial_observation,
            "outcome": visit.outcome,
            "remarks": visit.remarks
        },
        "service_call": {
            "call_id": service_call.call_id,
            "status": service_call.status
        }
    }), 201


@engineer_visits_bp.get("")
def get_engineer_visits():
    visits = db.session.scalars(
        select(EngineerVisit)
        .order_by(EngineerVisit.id.desc())
    ).all()

    result = []

    for visit in visits:
        engineer = db.session.get(
            Engineer,
            visit.engineer_id
        )

        service_call = db.session.get(
            ServiceCall,
            visit.service_call_id
        )

        result.append({
            "id": visit.id,
            "visit_number": visit.visit_number,
            "service_call_id": visit.service_call_id,
            "call_id": (
                service_call.call_id
                if service_call
                else None
            ),
            "appointment_id": visit.appointment_id,
            "engineer_id": visit.engineer_id,
            "engineer_code": (
                engineer.engineer_code
                if engineer
                else None
            ),
            "engineer_name": (
                engineer.engineer_name
                if engineer
                else None
            ),
            "visit_date": visit.visit_date.isoformat(),
            "arrival_time": (
                visit.arrival_time.isoformat()
                if visit.arrival_time
                else None
            ),
            "departure_time": (
                visit.departure_time.isoformat()
                if visit.departure_time
                else None
            ),
            "customer_available": visit.customer_available,
            "observations": visit.observations,
            "initial_observation": visit.initial_observation,
            "part_required": visit.part_required,
            "outcome": visit.outcome,
            "status": visit.status,
            "revisit_required": visit.revisit_required,
            "remarks": visit.remarks
        })

    return jsonify(result), 200


@engineer_visits_bp.get("/<int:visit_id>")
def get_engineer_visit(visit_id):
    visit = db.session.get(
        EngineerVisit,
        visit_id
    )

    if not visit:
        return jsonify({
            "message": "Engineer visit not found"
        }), 404

    engineer = db.session.get(
        Engineer,
        visit.engineer_id
    )

    service_call = db.session.get(
        ServiceCall,
        visit.service_call_id
    )

    return jsonify({
        "id": visit.id,
        "visit_number": visit.visit_number,
        "service_call_id": visit.service_call_id,
        "call_id": (
            service_call.call_id
            if service_call
            else None
        ),
        "appointment_id": visit.appointment_id,
        "engineer_id": visit.engineer_id,
        "engineer_code": (
            engineer.engineer_code
            if engineer
            else None
        ),
        "engineer_name": (
            engineer.engineer_name
            if engineer
            else None
        ),
        "visit_date": visit.visit_date.isoformat(),
        "arrival_time": (
            visit.arrival_time.isoformat()
            if visit.arrival_time
            else None
        ),
        "departure_time": (
            visit.departure_time.isoformat()
            if visit.departure_time
            else None
        ),
        "customer_available": visit.customer_available,
        "observations": visit.observations,
        "initial_observation": visit.initial_observation,
        "part_required": visit.part_required,
        "outcome": visit.outcome,
        "status": visit.status,
        "revisit_required": visit.revisit_required,
        "remarks": visit.remarks
    }), 200


@engineer_visits_bp.put("/<int:visit_id>")
def update_engineer_visit(visit_id):
    visit = db.session.get(
        EngineerVisit,
        visit_id
    )

    if not visit:
        return jsonify({
            "message": "Engineer visit not found"
        }), 404

    data = request.get_json(silent=True) or {}

    if "arrival_time" in data:
        if data["arrival_time"]:
            try:
                visit.arrival_time = datetime.fromisoformat(
                    data["arrival_time"]
                )
            except ValueError:
                return jsonify({
                    "message": "arrival_time must be valid ISO datetime"
                }), 400
        else:
            visit.arrival_time = None

    if "departure_time" in data:
        if data["departure_time"]:
            try:
                visit.departure_time = datetime.fromisoformat(
                    data["departure_time"]
                )
            except ValueError:
                return jsonify({
                    "message": "departure_time must be valid ISO datetime"
                }), 400
        else:
            visit.departure_time = None

    allowed_fields = [
        "customer_available",
        "observations",
        "initial_observation",
        "part_required",
        "outcome",
        "status",
        "revisit_required",
        "remarks"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(
                visit,
                field,
                data[field]
            )

    db.session.commit()

    return jsonify({
        "message": "Engineer visit updated successfully",
        "visit": {
            "id": visit.id,
            "visit_number": visit.visit_number,
            "status": visit.status,
            "customer_available": visit.customer_available,
            "part_required": visit.part_required,
            "revisit_required": visit.revisit_required,
            "outcome": visit.outcome
        }
    }), 200