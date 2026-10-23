from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select

from extensions import db
from models.asc import ASC
from models.asc_assignment import ASCAssignment
from models.service_call import ServiceCall
from models.engineer import Engineer


asc_assignments_bp = Blueprint(
    "asc_assignments",
    __name__,
    url_prefix="/api/asc-assignments"
)


def utc_now():
    return datetime.now(timezone.utc)


def get_active_assignment(service_call_id):
    return db.session.scalar(
        select(ASCAssignment)
        .where(
            ASCAssignment.service_call_id == service_call_id,
            ASCAssignment.assignment_status == "Assigned"
        )
        .order_by(ASCAssignment.id.desc())
    )


def assignment_json(assignment):
    asc = db.session.get(ASC, assignment.asc_id)
    service_call = db.session.get(
        ServiceCall, assignment.service_call_id
    )

    engineer = None
    if service_call and service_call.engineer_id:
        engineer = db.session.get(
            Engineer, service_call.engineer_id
        )

    return {
        "id": assignment.id,
        "service_call_id": assignment.service_call_id,
        "call_id": service_call.call_id if service_call else None,
        "complaint_id": (
            service_call.complaint_id if service_call else None
        ),
        "asc_id": assignment.asc_id,
        "asc_code": asc.asc_code if asc else None,
        "asc_name": asc.asc_name if asc else None,
        "assignment_status": assignment.assignment_status,
        "assigned_at": (
            assignment.assigned_at.isoformat()
            if assignment.assigned_at else None
        ),
        "remarks": assignment.remarks,
        "engineer_id": engineer.id if engineer else None,
        "engineer_code": (
            engineer.engineer_code if engineer else None
        ),
        "engineer_name": (
            engineer.engineer_name if engineer else None
        ),
        "engineer_assignment_remarks": (
            service_call.engineer_assignment_remarks
            if service_call else None
        ),
        "engineer_assigned_at": (
            service_call.engineer_assigned_at.isoformat()
            if service_call and service_call.engineer_assigned_at
            else None
        )
    }


# =========================================================
# ASSIGN ASC
# POST /api/asc-assignments
# =========================================================

@asc_assignments_bp.post("")
def assign_asc():
    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    asc_id = data.get("asc_id")
    remarks = (data.get("remarks") or "").strip()

    if service_call_id in (None, "") or asc_id in (None, ""):
        return jsonify({
            "message": "service_call_id and asc_id are required"
        }), 400

    try:
        service_call_id = int(service_call_id)
        asc_id = int(asc_id)
    except (TypeError, ValueError):
        return jsonify({
            "message": "service_call_id and asc_id must be valid IDs"
        }), 400

    try:
        service_call = db.session.get(ServiceCall, service_call_id)
        if not service_call:
            return jsonify({"message": "Service call not found"}), 404

        asc = db.session.get(ASC, asc_id)
        if not asc:
            return jsonify({"message": "ASC not found"}), 404

        if asc.status != "Active":
            return jsonify({
                "message": "Cannot assign an inactive ASC",
                "asc_id": asc.id,
                "status": asc.status
            }), 400

        existing = get_active_assignment(service_call_id)

        if existing:
            if existing.asc_id == asc_id:
                return jsonify({
                    "message": "This service call is already assigned to the selected ASC",
                    "assignment": assignment_json(existing)
                }), 200

            return jsonify({
                "message": "Service call is already assigned to another ASC",
                "assignment_id": existing.id,
                "asc_id": existing.asc_id
            }), 409

        assignment = ASCAssignment(
            service_call_id=service_call_id,
            asc_id=asc_id,
            assignment_status="Assigned",
            assigned_at=utc_now(),
            remarks=remarks or None
        )

        db.session.add(assignment)
        service_call.status = "Assigned"
        db.session.commit()

        return jsonify({
            "message": "ASC assigned successfully",
            "assignment": assignment_json(assignment)
        }), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception("ASC assignment failed")
        return jsonify({
            "message": "Could not assign ASC due to a server error"
        }), 500


# =========================================================
# GET ALL ASC ASSIGNMENTS
# GET /api/asc-assignments
# =========================================================

@asc_assignments_bp.get("")
def get_assignments():
    assignments = db.session.scalars(
        select(ASCAssignment).order_by(
            ASCAssignment.id.desc()
        )
    ).all()

    return jsonify([
        assignment_json(assignment)
        for assignment in assignments
    ]), 200


# =========================================================
# GET SINGLE ASC ASSIGNMENT
# GET /api/asc-assignments/<assignment_id>
# =========================================================

@asc_assignments_bp.get("/<int:assignment_id>")
def get_assignment(assignment_id):
    assignment = db.session.get(
        ASCAssignment, assignment_id
    )

    if not assignment:
        return jsonify({
            "message": "ASC assignment not found"
        }), 404

    return jsonify(assignment_json(assignment)), 200


# =========================================================
# ASSIGN ENGINEER
# POST /api/asc-assignments/service-calls/<id>/assign-engineer
#
# Payload:
# {
#   "asc_id": 1,
#   "engineer_id": 1,
#   "remarks": "Assigned from dashboard"
# }
#
# If asc_id is provided and no active ASC assignment exists,
# create it first. If one exists for another ASC, do not
# silently change it.
# =========================================================

@asc_assignments_bp.post(
    "/service-calls/<int:service_call_id>/assign-engineer"
)
def assign_engineer(service_call_id):
    data = request.get_json(silent=True) or {}

    engineer_id = data.get("engineer_id")
    asc_id = data.get("asc_id")
    remarks = (
        data.get("remarks") or "Assigned to engineer"
    ).strip()

    if engineer_id in (None, ""):
        return jsonify({
            "message": "engineer_id is required"
        }), 400

    try:
        engineer_id = int(engineer_id)
        if asc_id not in (None, ""):
            asc_id = int(asc_id)
        else:
            asc_id = None
    except (TypeError, ValueError):
        return jsonify({
            "message": "asc_id and engineer_id must be valid IDs"
        }), 400

    try:
        service_call = db.session.get(
            ServiceCall, service_call_id
        )

        if not service_call:
            return jsonify({
                "message": "Service call not found"
            }), 404

        if service_call.status in ("Closed", "Cancelled"):
            return jsonify({
                "message": "Closed or cancelled calls cannot be assigned",
                "current_status": service_call.status
            }), 409

        engineer = db.session.get(Engineer, engineer_id)

        if not engineer:
            return jsonify({
                "message": "Engineer not found"
            }), 404

        if engineer.status != "Active":
            return jsonify({
                "message": "Cannot assign an inactive engineer",
                "engineer_id": engineer.id,
                "status": engineer.status
            }), 400

        asc_assignment = get_active_assignment(service_call_id)

        # Support both flows:
        # 1. Existing ASC assignment + engineer selection.
        # 2. ASC and engineer selected together in the dashboard.
        if asc_assignment:
            if asc_id is not None and asc_assignment.asc_id != asc_id:
                return jsonify({
                    "message": (
                        "This call is already assigned to another ASC. "
                        "Resolve the existing assignment before changing ASC."
                    ),
                    "existing_asc_id": asc_assignment.asc_id,
                    "requested_asc_id": asc_id
                }), 409

            selected_asc_id = asc_assignment.asc_id

        else:
            if asc_id is None:
                return jsonify({
                    "message": (
                        "No ASC is assigned to this call. "
                        "Select an ASC before assigning an engineer."
                    )
                }), 400

            selected_asc = db.session.get(ASC, asc_id)

            if not selected_asc:
                return jsonify({
                    "message": "ASC not found"
                }), 404

            if selected_asc.status != "Active":
                return jsonify({
                    "message": "Cannot assign an inactive ASC",
                    "status": selected_asc.status
                }), 400

            selected_asc_id = selected_asc.id

        if engineer.asc_id != selected_asc_id:
            return jsonify({
                "message": "Selected engineer does not belong to the selected ASC",
                "engineer_asc_id": engineer.asc_id,
                "selected_asc_id": selected_asc_id
            }), 400

        # Create the ASC assignment only when one does not exist.
        if not asc_assignment:
            asc_assignment = ASCAssignment(
                service_call_id=service_call_id,
                asc_id=selected_asc_id,
                assignment_status="Assigned",
                assigned_at=utc_now(),
                remarks=remarks or None
            )
            db.session.add(asc_assignment)
            db.session.flush()

        service_call.engineer_id = engineer.id
        service_call.engineer_assignment_remarks = remarks
        service_call.engineer_assigned_at = utc_now()
        service_call.status = "Assigned"

        db.session.commit()

        return jsonify({
            "message": "ASC and engineer assigned successfully",
            "service_call": {
                "id": service_call.id,
                "call_id": service_call.call_id,
                "complaint_id": service_call.complaint_id,
                "status": service_call.status,
                "bucket": service_call.status
            },
            "assignment": assignment_json(asc_assignment),
            "engineer": {
                "id": engineer.id,
                "engineer_id": engineer.id,
                "engineer_code": engineer.engineer_code,
                "engineer_name": engineer.engineer_name,
                "asc_id": engineer.asc_id
            },
            "remarks": service_call.engineer_assignment_remarks,
            "engineer_assigned_at": (
                service_call.engineer_assigned_at.isoformat()
                if service_call.engineer_assigned_at else None
            )
        }), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Engineer assignment failed for service call %s",
            service_call_id
        )
        return jsonify({
            "message": "Could not assign engineer due to a server error"
        }), 500


# =========================================================
# UPDATE SERVICE-CALL WORKFLOW
# POST /api/asc-assignments/service-calls/<id>/update
#
# Actions:
# Complete / Close Call
# Part Pending
# Cancel
# Revisit
# =========================================================

@asc_assignments_bp.post(
    "/service-calls/<int:service_call_id>/update"
)
def update_service_call_workflow(service_call_id):
    data = request.get_json(silent=True) or {}

    action = str(
        data.get("action") or data.get("status") or ""
    ).strip()

    remarks = str(data.get("remarks") or "").strip()

    service_call = db.session.get(
        ServiceCall, service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    if service_call.status in ("Closed", "Cancelled"):
        return jsonify({
            "message": "Closed or cancelled service calls cannot be updated",
            "current_status": service_call.status
        }), 409

    if not action:
        return jsonify({
            "message": "Update action is required",
            "allowed_actions": [
                "Complete / Close Call",
                "Part Pending",
                "Cancel",
                "Revisit"
            ]
        }), 400

    normalized = action.lower().strip()

    # -----------------------------------------------------
    # CLOSE CALL
    # -----------------------------------------------------

    if normalized in (
        "complete",
        "close",
        "close call",
        "complete / close call"
    ):
        if service_call.status != "Customer Confirmation":
            return jsonify({
                "message": (
                    "Call cannot be closed yet. Complete Diagnosis, "
                    "Repair, Testing and Customer Confirmation first."
                ),
                "current_status": service_call.status,
                "required_before_close": [
                    "Diagnosis",
                    "Repair",
                    "Testing",
                    "Customer Confirmation",
                    "Happy Code"
                ]
            }), 409

        try:
            from models.customer_confirmation import CustomerConfirmation

            confirmation = db.session.scalar(
                select(CustomerConfirmation)
                .where(
                    CustomerConfirmation.service_call_id
                    == service_call_id
                )
                .order_by(CustomerConfirmation.id.desc())
            )
        except ImportError:
            current_app.logger.exception(
                "CustomerConfirmation model could not be imported"
            )
            return jsonify({
                "message": "Customer confirmation model is unavailable"
            }), 500

        if not confirmation:
            return jsonify({
                "message": "Customer confirmation is required before closing",
                "missing": ["Customer Confirmation"]
            }), 409

        confirmation_status = str(
            getattr(confirmation, "status", "") or ""
        ).strip().lower()

        if confirmation_status not in (
            "accepted",
            "confirmed",
            "complete",
            "completed"
        ):
            return jsonify({
                "message": "Customer confirmation is not completed",
                "confirmation_status": getattr(
                    confirmation, "status", None
                )
            }), 409

        happy_code = getattr(confirmation, "happy_code", None)

        if not happy_code:
            return jsonify({
                "message": "Happy Code is required before closing",
                "missing": ["Happy Code"]
            }), 409

        previous_status = service_call.status
        service_call.status = "Closed"

        if remarks:
            service_call.engineer_assignment_remarks = remarks

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to close service call %s", service_call_id
            )
            return jsonify({
                "message": "Could not close the service call"
            }), 500

        return jsonify({
            "message": "Service call closed successfully",
            "service_call": {
                "id": service_call.id,
                "call_id": service_call.call_id,
                "complaint_id": service_call.complaint_id,
                "previous_status": previous_status,
                "status": service_call.status,
                "bucket": "Closed"
            }
        }), 200

    # -----------------------------------------------------
    # PART PENDING
    # -----------------------------------------------------

    if normalized in (
        "part pending",
        "part_required",
        "part required"
    ):
        previous_status = service_call.status
        service_call.status = "Part Pending"

        if remarks:
            service_call.engineer_assignment_remarks = remarks

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update Part Pending for call %s",
                service_call_id
            )
            return jsonify({
                "message": "Could not update service call"
            }), 500

        return jsonify({
            "message": "Service call moved to Part Pending",
            "service_call": {
                "id": service_call.id,
                "call_id": service_call.call_id,
                "complaint_id": service_call.complaint_id,
                "previous_status": previous_status,
                "status": service_call.status,
                "bucket": service_call.status
            },
            "remarks": remarks
        }), 200

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    if normalized in (
        "cancel",
        "cancel call",
        "call cancel",
        "cancelled"
    ):
        if not remarks:
            return jsonify({
                "message": "Cancellation reason/remarks are required",
                "missing": ["Cancellation Reason"]
            }), 400

        previous_status = service_call.status
        service_call.status = "Cancelled"
        service_call.engineer_assignment_remarks = remarks

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to cancel service call %s", service_call_id
            )
            return jsonify({
                "message": "Could not cancel service call"
            }), 500

        return jsonify({
            "message": "Service call cancelled successfully",
            "service_call": {
                "id": service_call.id,
                "call_id": service_call.call_id,
                "complaint_id": service_call.complaint_id,
                "previous_status": previous_status,
                "status": service_call.status,
                "bucket": service_call.status
            },
            "remarks": remarks
        }), 200

    # -----------------------------------------------------
    # REVISIT
    # -----------------------------------------------------

    if normalized in ("revisit", "re-visit"):
        if not remarks:
            return jsonify({
                "message": "Revisit reason/remarks are required",
                "missing": ["Revisit Reason"]
            }), 400

        previous_status = service_call.status
        service_call.status = "Revisit"
        service_call.engineer_assignment_remarks = remarks

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to mark service call for revisit %s",
                service_call_id
            )
            return jsonify({
                "message": "Could not update service call"
            }), 500

        return jsonify({
            "message": "Service call moved to Revisit",
            "service_call": {
                "id": service_call.id,
                "call_id": service_call.call_id,
                "complaint_id": service_call.complaint_id,
                "previous_status": previous_status,
                "status": service_call.status,
                "bucket": service_call.status
            },
            "remarks": remarks
        }), 200

    return jsonify({
        "message": "Invalid update action",
        "received_action": action,
        "allowed_actions": [
            "Complete / Close Call",
            "Part Pending",
            "Cancel",
            "Revisit"
        ]
    }), 400