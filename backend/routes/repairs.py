from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.repair import Repair
from models.service_call import ServiceCall
from models.engineer_visit import EngineerVisit
from models.diagnosis import Diagnosis
from models.repair_code import RepairCode


repairs_bp = Blueprint(
    "repairs",
    __name__,
    url_prefix="/api/repairs"
)


REPAIR_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
    "Cancelled"
]


def repair_response(repair):
    service_call = db.session.get(
        ServiceCall,
        repair.service_call_id
    )

    return {
        "id": repair.id,
        "repair_number": repair.repair_number,
        "service_call_id": repair.service_call_id,
        "call_id": (
            service_call.call_id
            if service_call
            else None
        ),
        "visit_id": repair.visit_id,
        "diagnosis_id": repair.diagnosis_id,
        "repair_code_id": repair.repair_code_id,
        "part_required": repair.part_required,
        "actual_repair_action": repair.actual_repair_action,
        "repair_result": repair.repair_result,
        "skill_required": repair.skill_required,
        "status": repair.status,
        "testing_required": repair.testing_required,
        "remarks": repair.remarks
    }


@repairs_bp.post("")
def create_repair():
    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    visit_id = data.get("visit_id")
    diagnosis_id = data.get("diagnosis_id")
    repair_code_id = data.get("repair_code_id")

    if not service_call_id:
        return jsonify({
            "message": "service_call_id is required"
        }), 400

    if not visit_id:
        return jsonify({
            "message": "visit_id is required"
        }), 400

    if not diagnosis_id:
        return jsonify({
            "message": "diagnosis_id is required"
        }), 400

    if not repair_code_id:
        return jsonify({
            "message": "repair_code_id is required"
        }), 400

    service_call = db.session.get(
        ServiceCall,
        service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    visit = db.session.get(
        EngineerVisit,
        visit_id
    )

    if not visit:
        return jsonify({
            "message": "Engineer visit not found"
        }), 404

    if visit.service_call_id != service_call_id:
        return jsonify({
            "message": "Engineer visit does not belong to this service call"
        }), 400

    diagnosis = db.session.get(
        Diagnosis,
        diagnosis_id
    )

    if not diagnosis:
        return jsonify({
            "message": "Diagnosis not found"
        }), 404

    if diagnosis.service_call_id != service_call_id:
        return jsonify({
            "message": "Diagnosis does not belong to this service call"
        }), 400

    repair_code = db.session.get(
        RepairCode,
        repair_code_id
    )

    if not repair_code:
        return jsonify({
            "message": "Repair code not found"
        }), 404

    last_repair = db.session.scalar(
        select(Repair)
        .order_by(Repair.id.desc())
        .limit(1)
    )

    next_number = (
        1
        if not last_repair
        else last_repair.id + 1
    )

    repair_number = f"REP-{next_number:04d}"

    repair = Repair(
        repair_number=repair_number,
        service_call_id=service_call_id,
        visit_id=visit_id,
        diagnosis_id=diagnosis_id,
        repair_code_id=repair_code_id,
        part_required=data.get(
            "part_required",
            False
        ),
        actual_repair_action=data.get(
            "actual_repair_action"
        ),
        repair_result=data.get(
            "repair_result"
        ),
        skill_required=data.get(
            "skill_required"
        ),
        status=data.get(
            "status",
            "Pending"
        ),
        testing_required=data.get(
            "testing_required",
            True
        ),
        remarks=data.get("remarks")
    )

    db.session.add(repair)

    service_call.status = "Repair In Progress"

    db.session.commit()

    return jsonify({
        "message": "Repair created successfully",
        "repair": repair_response(repair)
    }), 201


@repairs_bp.get("")
def get_repairs():
    repairs = db.session.scalars(
        select(Repair)
        .order_by(Repair.id.desc())
    ).all()

    return jsonify([
        repair_response(repair)
        for repair in repairs
    ]), 200


@repairs_bp.get("/<int:repair_id>")
def get_repair(repair_id):
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    return jsonify(
        repair_response(repair)
    ), 200


@repairs_bp.post("/<int:repair_id>/start")
def start_repair(repair_id):
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    if repair.status != "Pending":
        return jsonify({
            "message": (
                f"Repair cannot be started from status "
                f"'{repair.status}'"
            )
        }), 409

    service_call = db.session.get(
        ServiceCall,
        repair.service_call_id
    )

    repair.status = "In Progress"

    if service_call:
        service_call.status = "Repair In Progress"

    db.session.commit()

    return jsonify({
        "message": "Repair started successfully",
        "repair": repair_response(repair)
    }), 200


@repairs_bp.post("/<int:repair_id>/complete")
def complete_repair(repair_id):
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    if repair.status != "In Progress":
        return jsonify({
            "message": (
                f"Repair cannot be completed from status "
                f"'{repair.status}'"
            )
        }), 409

    if not repair.actual_repair_action:
        return jsonify({
            "message": "actual_repair_action is required before completion"
        }), 400

    if not repair.repair_result:
        return jsonify({
            "message": "repair_result is required before completion"
        }), 400

    repair.status = "Completed"

    db.session.commit()

    return jsonify({
        "message": "Repair completed successfully",
        "repair": repair_response(repair)
    }), 200


@repairs_bp.post("/<int:repair_id>/cancel")
def cancel_repair(repair_id):
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    if repair.status == "Completed":
        return jsonify({
            "message": "Completed repair cannot be cancelled"
        }), 409

    if repair.status == "Cancelled":
        return jsonify({
            "message": "Repair is already cancelled"
        }), 409

    repair.status = "Cancelled"

    db.session.commit()

    return jsonify({
        "message": "Repair cancelled successfully",
        "repair": repair_response(repair)
    }), 200


@repairs_bp.put("/<int:repair_id>")
def update_repair(repair_id):
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    data = request.get_json(silent=True) or {}

    allowed_fields = [
        "part_required",
        "actual_repair_action",
        "repair_result",
        "skill_required",
        "testing_required",
        "remarks"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(
                repair,
                field,
                data[field]
            )

    db.session.commit()

    return jsonify({
        "message": "Repair details updated successfully",
        "repair": repair_response(repair)
    }), 200