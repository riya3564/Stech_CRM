from flask import Blueprint, request, jsonify
from datetime import datetime

from extensions import db
from models.testing import Testing
from models.repair import Repair
from models.engineer import Engineer


testing_bp = Blueprint(
    "testing",
    __name__,
    url_prefix="/api/testing"
)


# =========================================================
# CREATE TESTING
# =========================================================
@testing_bp.post("")
def create_testing():

    data = request.get_json(silent=True) or {}

    repair_id = data.get("repair_id")
    tested_by = data.get("tested_by")
    remarks = data.get("remarks")

    # -----------------------------------------------------
    # Required field
    # -----------------------------------------------------
    if not repair_id:
        return jsonify({
            "error": "repair_id is required"
        }), 400

    # -----------------------------------------------------
    # Find repair
    # -----------------------------------------------------
    repair = db.session.get(
        Repair,
        repair_id
    )

    if not repair:
        return jsonify({
            "error": "Repair not found"
        }), 404

    # -----------------------------------------------------
    # Repair must be completed before testing
    # -----------------------------------------------------
    if repair.status != "Completed":
        return jsonify({
            "error": (
                f"Testing cannot be started while repair "
                f"status is '{repair.status}'"
            )
        }), 409

    # -----------------------------------------------------
    # Validate engineer if provided
    # -----------------------------------------------------
    if tested_by:

        engineer = db.session.get(
            Engineer,
            tested_by
        )

        if not engineer:
            return jsonify({
                "error": "Engineer not found"
            }), 404

    # -----------------------------------------------------
    # Check latest testing
    # -----------------------------------------------------
    latest_testing = Testing.query.filter_by(
        repair_id=repair_id
    ).order_by(
        Testing.id.desc()
    ).first()

    # Do not allow duplicate pending testing
    if latest_testing and latest_testing.status == "PENDING":
        return jsonify({
            "error": "Testing already pending for this repair",
            "testing_code": latest_testing.testing_code
        }), 409

    # -----------------------------------------------------
    # Generate testing number
    # -----------------------------------------------------
    last_testing = Testing.query.order_by(
        Testing.id.desc()
    ).first()

    next_number = 1

    if last_testing:
        next_number = last_testing.id + 1

    testing_code = f"TEST-{next_number:04d}"

    # -----------------------------------------------------
    # Create testing
    # -----------------------------------------------------
    testing = Testing(
        testing_code=testing_code,
        repair_id=repair_id,
        status="PENDING",
        remarks=remarks,
        tested_by=tested_by
    )

    db.session.add(testing)
    db.session.commit()

    return jsonify({
        "message": "Testing created successfully",
        "testing": {
            "id": testing.id,
            "testing_code": testing.testing_code,
            "repair_id": testing.repair_id,
            "status": testing.status,
            "remarks": testing.remarks,
            "tested_by": testing.tested_by,
            "tested_at": testing.tested_at,
            "created_at": testing.created_at
        }
    }), 201


# =========================================================
# GET ALL TESTINGS
# =========================================================
@testing_bp.get("")
def get_testings():

    testings = Testing.query.order_by(
        Testing.id.desc()
    ).all()

    result = []

    for testing in testings:

        result.append({
            "id": testing.id,
            "testing_code": testing.testing_code,
            "repair_id": testing.repair_id,
            "status": testing.status,
            "remarks": testing.remarks,
            "tested_by": testing.tested_by,
            "tested_at": testing.tested_at,
            "created_at": testing.created_at,
            "updated_at": testing.updated_at
        })

    return jsonify({
        "count": len(result),
        "testings": result
    }), 200


# =========================================================
# GET SINGLE TESTING
# =========================================================
@testing_bp.get("/<int:testing_id>")
def get_testing(testing_id):

    testing = db.session.get(
        Testing,
        testing_id
    )

    if not testing:
        return jsonify({
            "error": "Testing record not found"
        }), 404

    return jsonify({
        "id": testing.id,
        "testing_code": testing.testing_code,
        "repair_id": testing.repair_id,
        "status": testing.status,
        "remarks": testing.remarks,
        "tested_by": testing.tested_by,
        "tested_at": testing.tested_at,
        "created_at": testing.created_at,
        "updated_at": testing.updated_at
    }), 200


# =========================================================
# UPDATE TESTING RESULT
# =========================================================
@testing_bp.put("/<int:testing_id>")
def update_testing(testing_id):

    testing = db.session.get(
        Testing,
        testing_id
    )

    if not testing:
        return jsonify({
            "error": "Testing record not found"
        }), 404

    data = request.get_json(silent=True) or {}

    status = data.get("status")
    remarks = data.get("remarks")
    tested_by = data.get("tested_by")

    # -----------------------------------------------------
    # Validate status
    # -----------------------------------------------------
    if status:

        status = status.upper()

        allowed_statuses = [
            "PENDING",
            "PASS",
            "FAIL"
        ]

        if status not in allowed_statuses:
            return jsonify({
                "error": "Invalid testing status",
                "allowed_statuses": allowed_statuses
            }), 400

        # -------------------------------------------------
        # Completed result cannot be changed
        # -------------------------------------------------
        if (
            testing.status in ["PASS", "FAIL"]
            and status != testing.status
        ):
            return jsonify({
                "error": (
                    "Completed testing result cannot be changed"
                )
            }), 409

        testing.status = status

        # -------------------------------------------------
        # Completion timestamp
        # -------------------------------------------------
        if status in ["PASS", "FAIL"]:
            testing.tested_at = datetime.utcnow()

    # -----------------------------------------------------
    # Update remarks
    # -----------------------------------------------------
    if remarks is not None:
        testing.remarks = remarks

    # -----------------------------------------------------
    # Update engineer
    # -----------------------------------------------------
    if tested_by is not None:

        engineer = db.session.get(
            Engineer,
            tested_by
        )

        if not engineer:
            return jsonify({
                "error": "Engineer not found"
            }), 404

        testing.tested_by = tested_by

    db.session.commit()

    return jsonify({
        "message": "Testing updated successfully",
        "testing": {
            "id": testing.id,
            "testing_code": testing.testing_code,
            "repair_id": testing.repair_id,
            "status": testing.status,
            "remarks": testing.remarks,
            "tested_by": testing.tested_by,
            "tested_at": testing.tested_at,
            "updated_at": testing.updated_at
        }
    }), 200


# =========================================================
# DELETE TESTING
# =========================================================
@testing_bp.delete("/<int:testing_id>")
def delete_testing(testing_id):

    testing = db.session.get(
        Testing,
        testing_id
    )

    if not testing:
        return jsonify({
            "error": "Testing record not found"
        }), 404

    db.session.delete(testing)
    db.session.commit()

    return jsonify({
        "message": "Testing deleted successfully"
    }), 200