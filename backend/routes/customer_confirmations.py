from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.customer_confirmation import CustomerConfirmation
from models.service_call import ServiceCall
from models.repair import Repair
from models.testing import Testing


customer_confirmations_bp = Blueprint(
    "customer_confirmations",
    __name__,
    url_prefix="/api/customer-confirmations"
)


CONFIRMATION_STATUSES = [
    "PENDING",
    "ACCEPTED",
    "REJECTED"
]


def confirmation_response(confirmation):

    service_call = db.session.get(
        ServiceCall,
        confirmation.service_call_id
    )

    return {
        "id": confirmation.id,
        "confirmation_code": confirmation.confirmation_code,
        "service_call_id": confirmation.service_call_id,
        "call_id": (
            service_call.call_id
            if service_call
            else None
        ),
        "repair_id": confirmation.repair_id,
        "testing_id": confirmation.testing_id,
        "status": confirmation.status,
        "confirmation_mode": confirmation.confirmation_mode,
        "happy_code": confirmation.happy_code,
        "customer_remarks": confirmation.customer_remarks,
        "confirmed_at": confirmation.confirmed_at,
        "created_at": confirmation.created_at,
        "updated_at": confirmation.updated_at
    }


# =========================================================
# CREATE CUSTOMER CONFIRMATION
# =========================================================
@customer_confirmations_bp.post("")
def create_customer_confirmation():

    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    repair_id = data.get("repair_id")
    testing_id = data.get("testing_id")

    if not service_call_id:
        return jsonify({
            "message": "service_call_id is required"
        }), 400

    if not repair_id:
        return jsonify({
            "message": "repair_id is required"
        }), 400

    if not testing_id:
        return jsonify({
            "message": "testing_id is required"
        }), 400

    service_call = db.session.get(
        ServiceCall,
        service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

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

    if repair.status != "Completed":
        return jsonify({
            "message": (
                "Customer confirmation cannot be created "
                f"while repair status is '{repair.status}'"
            )
        }), 409

    testing = db.session.get(
        Testing,
        testing_id
    )

    if not testing:
        return jsonify({
            "message": "Testing record not found"
        }), 404

    if testing.repair_id != repair_id:
        return jsonify({
            "message": (
                "Testing record does not belong to this repair"
            )
        }), 400

    if testing.status != "PASS":
        return jsonify({
            "message": (
                "Customer confirmation can only be created "
                "after testing PASS"
            ),
            "testing_status": testing.status
        }), 409

    if service_call.status != "Testing":
        return jsonify({
            "message": (
                "Customer confirmation cannot be created "
                f"while service call status is '{service_call.status}'"
            )
        }), 409

    existing = db.session.scalar(
        select(CustomerConfirmation)
        .where(
            CustomerConfirmation.repair_id == repair_id,
            CustomerConfirmation.status == "PENDING"
        )
        .limit(1)
    )

    if existing:
        return jsonify({
            "message": (
                "Customer confirmation is already pending "
                "for this repair"
            ),
            "confirmation": confirmation_response(existing)
        }), 409

    last_confirmation = db.session.scalar(
        select(CustomerConfirmation)
        .order_by(CustomerConfirmation.id.desc())
        .limit(1)
    )

    next_number = (
        1
        if not last_confirmation
        else last_confirmation.id + 1
    )

    confirmation_code = f"CONF-{next_number:04d}"

    confirmation = CustomerConfirmation(
        confirmation_code=confirmation_code,
        service_call_id=service_call_id,
        repair_id=repair_id,
        testing_id=testing_id,
        status="PENDING",
        confirmation_mode=data.get("confirmation_mode"),
        happy_code=None,
        customer_remarks=data.get("customer_remarks")
    )

    db.session.add(confirmation)

    service_call.status = "Customer Confirmation"

    db.session.commit()

    return jsonify({
        "message": "Customer confirmation created successfully",
        "confirmation": confirmation_response(confirmation)
    }), 201


# =========================================================
# GET ALL CUSTOMER CONFIRMATIONS
# =========================================================
@customer_confirmations_bp.get("")
def get_customer_confirmations():

    confirmations = db.session.scalars(
        select(CustomerConfirmation)
        .order_by(CustomerConfirmation.id.desc())
    ).all()

    return jsonify({
        "count": len(confirmations),
        "confirmations": [
            confirmation_response(confirmation)
            for confirmation in confirmations
        ]
    }), 200


# =========================================================
# GET SINGLE CUSTOMER CONFIRMATION
# =========================================================
@customer_confirmations_bp.get("/<int:confirmation_id>")
def get_customer_confirmation(confirmation_id):

    confirmation = db.session.get(
        CustomerConfirmation,
        confirmation_id
    )

    if not confirmation:
        return jsonify({
            "message": "Customer confirmation not found"
        }), 404

    return jsonify(
        confirmation_response(confirmation)
    ), 200


# =========================================================
# ACCEPT / REJECT CUSTOMER CONFIRMATION
# =========================================================
@customer_confirmations_bp.put("/<int:confirmation_id>")
def update_customer_confirmation(confirmation_id):

    confirmation = db.session.get(
        CustomerConfirmation,
        confirmation_id
    )

    if not confirmation:
        return jsonify({
            "message": "Customer confirmation not found"
        }), 404

    data = request.get_json(silent=True) or {}

    status = data.get("status")

    if not status:
        return jsonify({
            "message": "status is required",
            "allowed_statuses": [
                "ACCEPTED",
                "REJECTED"
            ]
        }), 400

    status = str(status).upper()

    if status not in [
        "ACCEPTED",
        "REJECTED"
    ]:
        return jsonify({
            "message": "Invalid confirmation status",
            "allowed_statuses": [
                "ACCEPTED",
                "REJECTED"
            ]
        }), 400

    if confirmation.status in [
        "ACCEPTED",
        "REJECTED"
    ]:
        return jsonify({
            "message": (
                "Customer confirmation has already been completed"
            ),
            "current_status": confirmation.status
        }), 409

    service_call = db.session.get(
        ServiceCall,
        confirmation.service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    # -----------------------------------------------------
    # HAPPY CODE REQUIRED FOR ACCEPTANCE
    # -----------------------------------------------------
    if status == "ACCEPTED":

        happy_code = data.get("happy_code")

        if not happy_code:
            return jsonify({
                "message": (
                    "Happy code is required before "
                    "customer confirmation can be accepted"
                )
            }), 400

        happy_code = str(happy_code).strip()

        if len(happy_code) < 4:
            return jsonify({
                "message": "Happy code must contain at least 4 characters"
            }), 400

        confirmation.happy_code = happy_code

    confirmation.status = status

    confirmation.confirmation_mode = data.get(
        "confirmation_mode",
        confirmation.confirmation_mode
    )

    confirmation.customer_remarks = data.get(
        "customer_remarks",
        confirmation.customer_remarks
    )

    confirmation.confirmed_at = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Customer accepted
    # -----------------------------------------------------
    if status == "ACCEPTED":

        service_call.status = "Closed"

    # -----------------------------------------------------
    # Customer rejected
    # -----------------------------------------------------
    elif status == "REJECTED":

        service_call.status = "Revisit"

    db.session.commit()

    return jsonify({
        "message": (
            "Customer confirmation updated successfully"
        ),
        "confirmation": confirmation_response(
            confirmation
        ),
        "service_call": {
            "id": service_call.id,
            "call_id": service_call.call_id,
            "status": service_call.status
        }
    }), 200
