from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.appointment import Appointment
from models.service_call import ServiceCall
from models.asc import ASC
from models.engineer import Engineer


appointments_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/api/appointments"
)


@appointments_bp.post("")
def create_appointment():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "service_call_id",
        "asc_id",
        "engineer_id",
        "appointment_date",
        "appointment_point"
    ]

    missing_fields = [
        field
        for field in required_fields
        if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "message": "Required fields are missing",
            "missing_fields": missing_fields
        }), 400

    service_call = db.session.get(
        ServiceCall,
        data["service_call_id"]
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    asc = db.session.get(
        ASC,
        data["asc_id"]
    )

    if not asc:
        return jsonify({
            "message": "ASC not found"
        }), 404

    if asc.status != "Active":
        return jsonify({
            "message": "Cannot schedule appointment with inactive ASC",
            "asc_code": asc.asc_code,
            "status": asc.status
        }), 400

    engineer = db.session.get(
        Engineer,
        data["engineer_id"]
    )

    if not engineer:
        return jsonify({
            "message": "Engineer not found"
        }), 404

    if engineer.status != "Active":
        return jsonify({
            "message": "Cannot schedule appointment with inactive engineer",
            "engineer_code": engineer.engineer_code,
            "status": engineer.status
        }), 400

    if engineer.asc_id != asc.id:
        return jsonify({
            "message": "Engineer does not belong to the selected ASC",
            "engineer_asc_id": engineer.asc_id,
            "selected_asc_id": asc.id
        }), 400

    existing_appointment = db.session.scalar(
        select(Appointment).where(
            Appointment.service_call_id == data["service_call_id"],
            Appointment.status.in_([
                "Scheduled",
                "Confirmed",
                "In Progress"
            ])
        )
    )

    if existing_appointment:
        return jsonify({
            "message": "An active appointment already exists for this service call",
            "appointment_id": existing_appointment.id
        }), 409

    appointment = Appointment(
        service_call_id=data["service_call_id"],
        asc_id=asc.id,
        engineer_id=engineer.id,
        appointment_date=data["appointment_date"],
        appointment_time=data.get("appointment_time"),
        appointment_point=data["appointment_point"],
        status="Scheduled",
        remarks=data.get("remarks"),
        scheduled_at=datetime.now(timezone.utc)
    )

    db.session.add(appointment)

    service_call.status = "Appointment Scheduled"

    db.session.commit()

    return jsonify({
        "message": "Appointment scheduled successfully",
        "appointment": {
            "id": appointment.id,
            "service_call_id": appointment.service_call_id,
            "call_id": service_call.call_id,
            "asc_id": appointment.asc_id,
            "asc_code": asc.asc_code,
            "asc_name": asc.asc_name,
            "engineer_id": appointment.engineer_id,
            "engineer_code": engineer.engineer_code,
            "engineer_name": engineer.engineer_name,
            "appointment_date": appointment.appointment_date.isoformat(),
            "appointment_time": appointment.appointment_time,
            "appointment_point": appointment.appointment_point,
            "status": appointment.status,
            "remarks": appointment.remarks
        },
        "service_call": {
            "call_id": service_call.call_id,
            "status": service_call.status
        }
    }), 201


@appointments_bp.get("")
def get_appointments():
    appointments = db.session.scalars(
        select(Appointment).order_by(
            Appointment.id.desc()
        )
    ).all()

    result = []

    for appointment in appointments:
        service_call = db.session.get(
            ServiceCall,
            appointment.service_call_id
        )

        asc = db.session.get(
            ASC,
            appointment.asc_id
        )

        engineer = db.session.get(
            Engineer,
            appointment.engineer_id
        )

        result.append({
            "id": appointment.id,
            "service_call_id": appointment.service_call_id,
            "call_id": (
                service_call.call_id
                if service_call else None
            ),
            "asc_id": appointment.asc_id,
            "asc_code": (
                asc.asc_code
                if asc else None
            ),
            "asc_name": (
                asc.asc_name
                if asc else None
            ),
            "engineer_id": appointment.engineer_id,
            "engineer_code": (
                engineer.engineer_code
                if engineer else None
            ),
            "engineer_name": (
                engineer.engineer_name
                if engineer else None
            ),
            "appointment_date": appointment.appointment_date.isoformat(),
            "appointment_time": appointment.appointment_time,
            "appointment_point": appointment.appointment_point,
            "status": appointment.status,
            "remarks": appointment.remarks
        })

    return jsonify(result), 200


@appointments_bp.get("/<int:appointment_id>")
def get_appointment(appointment_id):
    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    service_call = db.session.get(
        ServiceCall,
        appointment.service_call_id
    )

    asc = db.session.get(
        ASC,
        appointment.asc_id
    )

    engineer = db.session.get(
        Engineer,
        appointment.engineer_id
    )

    return jsonify({
        "id": appointment.id,
        "service_call_id": appointment.service_call_id,
        "call_id": (
            service_call.call_id
            if service_call else None
        ),
        "asc_id": appointment.asc_id,
        "asc_code": (
            asc.asc_code
            if asc else None
        ),
        "asc_name": (
            asc.asc_name
            if asc else None
        ),
        "engineer_id": appointment.engineer_id,
        "engineer_code": (
            engineer.engineer_code
            if engineer else None
        ),
        "engineer_name": (
            engineer.engineer_name
            if engineer else None
        ),
        "appointment_date": appointment.appointment_date.isoformat(),
        "appointment_time": appointment.appointment_time,
        "appointment_point": appointment.appointment_point,
        "status": appointment.status,
        "remarks": appointment.remarks
    }), 200


@appointments_bp.put("/<int:appointment_id>")
def update_appointment(appointment_id):
    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if not appointment:
        return jsonify({
            "message": "Appointment not found"
        }), 404

    data = request.get_json(silent=True) or {}

    if "appointment_date" in data:
        appointment.appointment_date = data["appointment_date"]

    if "appointment_time" in data:
        appointment.appointment_time = data["appointment_time"]

    if "appointment_point" in data:
        appointment.appointment_point = data["appointment_point"]

    if "status" in data:
        appointment.status = data["status"]

    if "remarks" in data:
        appointment.remarks = data["remarks"]

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully",
        "appointment_id": appointment.id,
        "status": appointment.status
    }), 200