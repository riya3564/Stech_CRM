from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.part_requirement import PartRequirement
from models.service_call import ServiceCall
from models.engineer_visit import EngineerVisit
from models.diagnosis import Diagnosis
from models.repair import Repair
from models.part import Part
from models.inventory import Inventory


part_requirements_bp = Blueprint(
    "part_requirements",
    __name__,
    url_prefix="/api/part-requirements"
)


ACTIVE_REQUIREMENT_STATUSES = [
    "Pending",
    "Approved",
    "Part Pending",
    "Allocated",
    "Dispatched",
    "Received"
]


def generate_requirement_number():
    last_requirement = db.session.scalar(
        select(PartRequirement)
        .order_by(PartRequirement.id.desc())
    )

    next_id = 1 if not last_requirement else last_requirement.id + 1

    return f"PART-REQ-{next_id:04d}"


def requirement_response(requirement):
    part = db.session.get(Part, requirement.part_id)

    service_call = db.session.get(
        ServiceCall,
        requirement.service_call_id
    )

    inventory = db.session.scalar(
        select(Inventory).where(
            Inventory.part_id == requirement.part_id
        )
    )

    return {
        "id": requirement.id,
        "requirement_number": requirement.requirement_number,
        "service_call_id": requirement.service_call_id,
        "call_id": service_call.call_id if service_call else None,
        "visit_id": requirement.visit_id,
        "diagnosis_id": requirement.diagnosis_id,
        "repair_id": requirement.repair_id,
        "part_id": requirement.part_id,
        "part_code": part.part_code if part else None,
        "part_name": part.part_name if part else None,
        "quantity": requirement.quantity,
        "required_reason": requirement.required_reason,
        "priority": requirement.priority,
        "status": requirement.status,
        "availability_status": requirement.availability_status,
        "requested_at": (
            requirement.requested_at.isoformat()
            if requirement.requested_at
            else None
        ),
        "remarks": requirement.remarks,
        "inventory": {
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "warehouse_name": inventory.warehouse_name,
            "status": inventory.status
        } if inventory else None
    }


@part_requirements_bp.post("")
def create_part_requirement():

    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    visit_id = data.get("visit_id")
    diagnosis_id = data.get("diagnosis_id")
    repair_id = data.get("repair_id")
    part_id = data.get("part_id")

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

    if not repair_id:
        return jsonify({
            "message": "repair_id is required"
        }), 400

    if not part_id:
        return jsonify({
            "message": "part_id is required"
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

    if diagnosis.visit_id != visit_id:
        return jsonify({
            "message": "Diagnosis does not belong to this engineer visit"
        }), 400

    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Repair not found"
        }), 404

    if repair.service_call_id != service_call_id:
        return jsonify({
            "message": "Repair does not belong to this service call"
        }), 400

    if repair.visit_id != visit_id:
        return jsonify({
            "message": "Repair does not belong to this engineer visit"
        }), 400

    if repair.diagnosis_id != diagnosis_id:
        return jsonify({
            "message": "Repair does not belong to this diagnosis"
        }), 400

    part = db.session.get(
        Part,
        part_id
    )

    if not part:
        return jsonify({
            "message": "Part not found"
        }), 404

    existing = db.session.scalar(
        select(PartRequirement).where(
            PartRequirement.service_call_id == service_call_id,
            PartRequirement.repair_id == repair_id,
            PartRequirement.part_id == part_id,
            PartRequirement.status.in_(
                ACTIVE_REQUIREMENT_STATUSES
            )
        )
    )

    if existing:
        return jsonify({
            "message": "Active part requirement already exists",
            "requirement_number": existing.requirement_number,
            "requirement_id": existing.id
        }), 409

    try:
        quantity = int(
            data.get("quantity", 1)
        )
    except (TypeError, ValueError):
        return jsonify({
            "message": "quantity must be an integer"
        }), 400

    if quantity < 1:
        return jsonify({
            "message": "quantity must be at least 1"
        }), 400

    requirement = PartRequirement(
        requirement_number=generate_requirement_number(),
        service_call_id=service_call_id,
        visit_id=visit_id,
        diagnosis_id=diagnosis_id,
        repair_id=repair_id,
        part_id=part_id,
        quantity=quantity,
        required_reason=data.get("required_reason"),
        priority=data.get("priority", "Normal"),
        status="Pending",
        availability_status="Checking",
        remarks=data.get("remarks")
    )

    db.session.add(requirement)

    service_call.status = "Part Required"

    db.session.commit()

    return jsonify({
        "message": "Part requirement created successfully",
        "part_requirement": requirement_response(requirement),
        "service_call": {
            "call_id": service_call.call_id,
            "status": service_call.status
        }
    }), 201


@part_requirements_bp.get("")
def get_part_requirements():

    requirements = db.session.scalars(
        select(PartRequirement)
        .order_by(PartRequirement.id.desc())
    ).all()

    return jsonify([
        requirement_response(requirement)
        for requirement in requirements
    ]), 200


@part_requirements_bp.get("/<int:requirement_id>")
def get_part_requirement(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    return jsonify(
        requirement_response(requirement)
    ), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/availability-check"
)
def check_availability(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    inventory = db.session.scalar(
        select(Inventory).where(
            Inventory.part_id == requirement.part_id
        )
    )

    if not inventory:
        requirement.availability_status = "Not Available"
        requirement.status = "Part Pending"

        db.session.commit()

        return jsonify({
            "message": "Part is not available in inventory",
            "availability_status": "Not Available",
            "status": "Part Pending",
            "part_requirement": requirement_response(requirement)
        }), 200

    free_quantity = (
        inventory.available_quantity
        - inventory.reserved_quantity
    )

    if (
        inventory.status != "Active"
        or free_quantity < requirement.quantity
    ):
        requirement.availability_status = "Not Available"
        requirement.status = "Part Pending"

        db.session.commit()

        return jsonify({
            "message": "Required quantity is not currently available",
            "availability_status": "Not Available",
            "status": "Part Pending",
            "available_quantity": max(free_quantity, 0),
            "required_quantity": requirement.quantity,
            "part_requirement": requirement_response(requirement)
        }), 200

    requirement.availability_status = "Available"

    db.session.commit()

    return jsonify({
        "message": "Part is available",
        "availability_status": "Available",
        "status": requirement.status,
        "available_quantity": free_quantity,
        "required_quantity": requirement.quantity,
        "part_requirement": requirement_response(requirement)
    }), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/approve"
)
def approve_part_requirement(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    if requirement.availability_status != "Available":
        return jsonify({
            "message": "Part must be available before approval"
        }), 400

    if requirement.status not in [
        "Pending",
        "Part Pending"
    ]:
        return jsonify({
            "message": (
                "Part requirement cannot be approved "
                "in its current status"
            ),
            "status": requirement.status
        }), 400

    requirement.status = "Approved"

    db.session.commit()

    return jsonify({
        "message": "Part requirement approved successfully",
        "part_requirement": requirement_response(requirement)
    }), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/allocate"
)
def allocate_part(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    if requirement.status != "Approved":
        return jsonify({
            "message": (
                "Part requirement must be Approved "
                "before allocation"
            ),
            "status": requirement.status
        }), 400

    inventory = db.session.scalar(
        select(Inventory).where(
            Inventory.part_id == requirement.part_id
        )
    )

    if not inventory:
        return jsonify({
            "message": "Inventory record not found"
        }), 404

    free_quantity = (
        inventory.available_quantity
        - inventory.reserved_quantity
    )

    if free_quantity < requirement.quantity:
        return jsonify({
            "message": "Insufficient available inventory",
            "available_quantity": free_quantity,
            "required_quantity": requirement.quantity
        }), 400

    inventory.reserved_quantity += requirement.quantity

    requirement.status = "Allocated"
    requirement.availability_status = "Available"

    db.session.commit()

    return jsonify({
        "message": "Part allocated successfully",
        "part_requirement": requirement_response(requirement),
        "inventory": {
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity
        }
    }), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/dispatch"
)
def dispatch_part(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    if requirement.status != "Allocated":
        return jsonify({
            "message": "Part must be Allocated before dispatch",
            "status": requirement.status
        }), 400

    requirement.status = "Dispatched"

    db.session.commit()

    return jsonify({
        "message": "Part dispatched successfully",
        "part_requirement": requirement_response(requirement)
    }), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/receive"
)
def receive_part(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    if requirement.status != "Dispatched":
        return jsonify({
            "message": "Part must be Dispatched before receiving",
            "status": requirement.status
        }), 400

    requirement.status = "Received"

    db.session.commit()

    return jsonify({
        "message": "Part received successfully",
        "part_requirement": requirement_response(requirement)
    }), 200


@part_requirements_bp.post(
    "/<int:requirement_id>/use"
)
def use_part(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    if requirement.status != "Received":
        return jsonify({
            "message": "Part must be Received before use",
            "status": requirement.status
        }), 400

    inventory = db.session.scalar(
        select(Inventory).where(
            Inventory.part_id == requirement.part_id
        )
    )

    if not inventory:
        return jsonify({
            "message": "Inventory record not found"
        }), 404

    if inventory.reserved_quantity < requirement.quantity:
        return jsonify({
            "message": "Reserved inventory is insufficient"
        }), 400

    if inventory.available_quantity < requirement.quantity:
        return jsonify({
            "message": "Available inventory is insufficient"
        }), 400

    # ---------------------------------------------------------
    # INVENTORY CONSUMPTION
    # ---------------------------------------------------------

    inventory.available_quantity -= requirement.quantity
    inventory.reserved_quantity -= requirement.quantity

    requirement.status = "Used"
    requirement.availability_status = "Used"

    # ---------------------------------------------------------
    # SERVICE CALL WORKFLOW UPDATE
    # Part has now been physically used in the repair.
    # ---------------------------------------------------------

    service_call = db.session.get(
        ServiceCall,
        requirement.service_call_id
    )

    if service_call:
        service_call.status = "Repair In Progress"

    db.session.commit()

    return jsonify({
        "message": "Part used successfully",
        "part_requirement": requirement_response(requirement),
        "inventory": {
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity
        },
        "service_call": {
            "call_id": service_call.call_id
            if service_call else None,
            "status": service_call.status
            if service_call else None
        }
    }), 200


@part_requirements_bp.put(
    "/<int:requirement_id>"
)
def update_part_requirement(requirement_id):

    requirement = db.session.get(
        PartRequirement,
        requirement_id
    )

    if not requirement:
        return jsonify({
            "message": "Part requirement not found"
        }), 404

    data = request.get_json(silent=True) or {}

    allowed_statuses = [
        "Pending",
        "Approved",
        "Part Pending",
        "Allocated",
        "Dispatched",
        "Received",
        "Used",
        "Cancelled"
    ]

    if "quantity" in data:

        try:
            quantity = int(data["quantity"])
        except (TypeError, ValueError):
            return jsonify({
                "message": "quantity must be an integer"
            }), 400

        if quantity < 1:
            return jsonify({
                "message": "quantity must be at least 1"
            }), 400

        requirement.quantity = quantity

    if "required_reason" in data:
        requirement.required_reason = data[
            "required_reason"
        ]

    if "priority" in data:
        requirement.priority = data["priority"]

    if "status" in data:

        if data["status"] not in allowed_statuses:
            return jsonify({
                "message": "Invalid part requirement status"
            }), 400

        requirement.status = data["status"]

    if "availability_status" in data:
        requirement.availability_status = data[
            "availability_status"
        ]

    if "remarks" in data:
        requirement.remarks = data["remarks"]

    db.session.commit()

    return jsonify({
        "message": "Part requirement updated successfully",
        "part_requirement": requirement_response(requirement)
    }), 200