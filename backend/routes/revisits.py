from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.revisit import Revisit
from models.service_call import ServiceCall


revisits_bp = Blueprint(
    "revisits",
    __name__,
    url_prefix="/api/revisits"
)


REVISIT_STATUSES = [
    "OPEN",
    "ASSIGNED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED"
]


def revisit_response(revisit):
    return {
        "id": revisit.id,
        "revisit_code": revisit.revisit_code,
        "service_call_id": revisit.service_call_id,
        "previous_service_call_id": revisit.previous_service_call_id,
        "reason": revisit.reason,
        "status": revisit.status,
        "priority": revisit.priority,
        "remarks": revisit.remarks,
        "created_at": revisit.created_at,
        "updated_at": revisit.updated_at
    }


# =========================================================
# CREATE REVISIT
# =========================================================
@revisits_bp.post("")
def create_revisit():

    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    reason = data.get("reason")

    if not service_call_id:
        return jsonify({
            "message": "service_call_id is required"
        }), 400

    if not reason:
        return jsonify({
            "message": "reason is required"
        }), 400

    service_call = db.session.get(
        ServiceCall,
        service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    # -----------------------------------------------------
    # Revisit should originate from a service call
    # having status "Revisit"
    # -----------------------------------------------------
    if service_call.status != "Revisit":
        return jsonify({
            "message": (
                "Revisit can only be created when "
                f"service call status is 'Revisit'. "
                f"Current status: '{service_call.status}'"
            )
        }), 409

    # -----------------------------------------------------
    # Prevent duplicate active revisit
    # -----------------------------------------------------
    existing = db.session.scalar(
        select(Revisit)
        .where(
            Revisit.service_call_id == service_call_id,
            Revisit.status.in_([
                "OPEN",
                "ASSIGNED",
                "IN_PROGRESS"
            ])
        )
        .limit(1)
    )

    if existing:
        return jsonify({
            "message": "An active revisit already exists",
            "revisit": revisit_response(existing)
        }), 409

    # -----------------------------------------------------
    # Generate revisit code
    # -----------------------------------------------------
    last_revisit = db.session.scalar(
        select(Revisit)
        .order_by(Revisit.id.desc())
        .limit(1)
    )

    next_number = (
        1
        if not last_revisit
        else last_revisit.id + 1
    )

    revisit_code = f"REV-{next_number:04d}"

    revisit = Revisit(
        revisit_code=revisit_code,
        service_call_id=service_call_id,
        previous_service_call_id=service_call_id,
        reason=str(reason).strip(),
        status="OPEN",
        priority=data.get(
            "priority",
            service_call.priority or "Normal"
        ),
        remarks=data.get("remarks")
    )

    db.session.add(revisit)
    db.session.commit()

    return jsonify({
        "message": "Revisit created successfully",
        "revisit": revisit_response(revisit)
    }), 201


# =========================================================
# GET ALL REVISITS
# =========================================================
@revisits_bp.get("")
def get_revisits():

    revisits = db.session.scalars(
        select(Revisit)
        .order_by(Revisit.id.desc())
    ).all()

    return jsonify({
        "count": len(revisits),
        "revisits": [
            revisit_response(revisit)
            for revisit in revisits
        ]
    }), 200


# =========================================================
# GET SINGLE REVISIT
# =========================================================
@revisits_bp.get("/<int:revisit_id>")
def get_revisit(revisit_id):

    revisit = db.session.get(
        Revisit,
        revisit_id
    )

    if not revisit:
        return jsonify({
            "message": "Revisit not found"
        }), 404

    return jsonify(
        revisit_response(revisit)
    ), 200


# =========================================================
# UPDATE REVISIT
# =========================================================
@revisits_bp.put("/<int:revisit_id>")
def update_revisit(revisit_id):

    revisit = db.session.get(
        Revisit,
        revisit_id
    )

    if not revisit:
        return jsonify({
            "message": "Revisit not found"
        }), 404

    data = request.get_json(silent=True) or {}

    status = data.get("status")

    if status:
        status = str(status).upper()

        if status not in REVISIT_STATUSES:
            return jsonify({
                "message": "Invalid revisit status",
                "allowed_statuses": REVISIT_STATUSES
            }), 400

        revisit.status = status

    if "priority" in data:
        revisit.priority = data.get("priority")

    if "remarks" in data:
        revisit.remarks = data.get("remarks")

    db.session.commit()

    return jsonify({
        "message": "Revisit updated successfully",
        "revisit": revisit_response(revisit)
    }), 200


# =========================================================
# COMPLETE REVISIT
# =========================================================
@revisits_bp.post("/<int:revisit_id>/complete")
def complete_revisit(revisit_id):

    revisit = db.session.get(
        Revisit,
        revisit_id
    )

    if not revisit:
        return jsonify({
            "message": "Revisit not found"
        }), 404

    if revisit.status != "IN_PROGRESS":
        return jsonify({
            "message": (
                "Revisit can only be completed "
                f"from IN_PROGRESS. "
                f"Current status: '{revisit.status}'"
            )
        }), 409

    revisit.status = "COMPLETED"

    db.session.commit()

    return jsonify({
        "message": "Revisit completed successfully",
        "revisit": revisit_response(revisit)
    }), 200


# =========================================================
# CANCEL REVISIT
# =========================================================
@revisits_bp.post("/<int:revisit_id>/cancel")
def cancel_revisit(revisit_id):

    revisit = db.session.get(
        Revisit,
        revisit_id
    )

    if not revisit:
        return jsonify({
            "message": "Revisit not found"
        }), 404

    if revisit.status in [
        "COMPLETED",
        "CANCELLED"
    ]:
        return jsonify({
            "message": (
                "Revisit cannot be cancelled "
                f"from status '{revisit.status}'"
            )
        }), 409

    revisit.status = "CANCELLED"

    db.session.commit()

    return jsonify({
        "message": "Revisit cancelled successfully",
        "revisit": revisit_response(revisit)
    }), 200