
from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.engineer import Engineer
from models.asc import ASC

engineers_bp = Blueprint(
    "engineers", __name__, url_prefix="/api/engineers"
)


def engineer_response(engineer):
    asc = db.session.get(ASC, engineer.asc_id)

    # Aadhaar is deliberately excluded from every response.
    return {
        "id": engineer.id,
        "engineer_code": engineer.engineer_code,
        "engineer_name": engineer.engineer_name,
        "asc_id": engineer.asc_id,
        "asc_code": asc.asc_code if asc else None,
        "asc_name": asc.asc_name if asc else None,
        "phone": engineer.phone,
        "alternate_phone": engineer.alternate_phone,
        "email": engineer.email,
        "address": engineer.address,
        "landmark": engineer.landmark,
        "locality": engineer.locality,
        "city": engineer.city,
        "district": engineer.district,
        "state": engineer.state,
        "pin_code": engineer.pin_code,
        "specialization": engineer.specialization,
        "service_area": engineer.service_area,
        "joining_date": (
            engineer.joining_date.isoformat()
            if engineer.joining_date else None
        ),
        "status": engineer.status,
    }


def clean_text(data, key, max_length=None):
    value = data.get(key)
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    if max_length and len(value) > max_length:
        raise ValueError(f"{key} must be {max_length} characters or fewer")
    return value


def validate_and_apply(engineer, data, creating=False):
    if creating or "engineer_code" in data:
        code = clean_text(data, "engineer_code", 50)
        if not code:
            raise ValueError("Engineer Code is required")
        code = code.upper()

        existing = db.session.scalar(
            select(Engineer).where(
                Engineer.engineer_code == code,
                Engineer.id != engineer.id if engineer.id else True,
            )
        )
        if existing:
            raise ValueError("Engineer Code already exists")
        engineer.engineer_code = code

    if creating or "engineer_name" in data:
        name = clean_text(data, "engineer_name", 150)
        if not name:
            raise ValueError("Engineer Name is required")
        engineer.engineer_name = name

    if creating or "asc_id" in data:
        raw_asc_id = data.get("asc_id")
        if raw_asc_id in (None, ""):
            raise ValueError("Service Center (ASC) is required")
        try:
            asc_id = int(raw_asc_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid ASC selection")

        asc = db.session.get(ASC, asc_id)
        if not asc:
            raise ValueError("Selected ASC was not found")
        if asc.status != "Active":
            raise ValueError("Select an active ASC")
        engineer.asc_id = asc.id

    text_fields = {
        "phone": 20,
        "alternate_phone": 20,
        "email": 150,
        "aadhaar_number": 12,
        "address": 250,
        "landmark": 150,
        "locality": 150,
        "city": 100,
        "district": 100,
        "state": 100,
        "pin_code": 10,
        "specialization": 200,
        "service_area": 200,
    }

    for field, max_length in text_fields.items():
        if field in data:
            value = clean_text(data, field, max_length)
            if field in ("phone", "alternate_phone") and value:
                digits = "".join(ch for ch in value if ch.isdigit())
                if len(digits) < 10 or len(digits) > 15:
                    raise ValueError(f"{field} must contain a valid phone number")
            if field == "aadhaar_number" and value:
                digits = "".join(ch for ch in value if ch.isdigit())
                if len(digits) != 12:
                    raise ValueError("Aadhaar number must contain 12 digits")
                value = digits
            if field == "pin_code" and value and (
                not value.isdigit() or len(value) != 6
            ):
                raise ValueError("PIN Code must contain 6 digits")
            setattr(engineer, field, value)

    if "joining_date" in data:
        raw_date = data.get("joining_date")
        if not raw_date:
            engineer.joining_date = None
        else:
            try:
                engineer.joining_date = date.fromisoformat(str(raw_date))
            except ValueError:
                raise ValueError("Joining Date must be YYYY-MM-DD")

    if creating:
        engineer.status = clean_text(data, "status", 20) or "Active"
    elif "status" in data:
        status = clean_text(data, "status", 20)
        if status not in ("Active", "Inactive"):
            raise ValueError("Status must be Active or Inactive")
        engineer.status = status


@engineers_bp.post("")
def create_engineer():
    data = request.get_json(silent=True) or {}
    engineer = Engineer()

    try:
        validate_and_apply(engineer, data, creating=True)
        db.session.add(engineer)
        db.session.commit()
        return jsonify({
            "message": "Engineer created successfully",
            "engineer": engineer_response(engineer),
        }), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "message": "Database error while creating engineer"
        }), 500


@engineers_bp.get("")
def get_engineers():
    engineers = db.session.scalars(
        select(Engineer).order_by(Engineer.id.asc())
    ).all()
    return jsonify([engineer_response(item) for item in engineers]), 200


@engineers_bp.get("/<int:engineer_id>")
def get_engineer(engineer_id):
    engineer = db.session.get(Engineer, engineer_id)
    if not engineer:
        return jsonify({"message": "Engineer not found"}), 404
    return jsonify(engineer_response(engineer)), 200


@engineers_bp.put("/<int:engineer_id>")
def update_engineer(engineer_id):
    engineer = db.session.get(Engineer, engineer_id)
    if not engineer:
        return jsonify({"message": "Engineer not found"}), 404

    data = request.get_json(silent=True) or {}
    try:
        validate_and_apply(engineer, data)
        db.session.commit()
        return jsonify({
            "message": "Engineer updated successfully",
            "engineer": engineer_response(engineer),
        }), 200
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "message": "Database error while updating engineer"
        }), 500
