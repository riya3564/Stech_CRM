from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.asc import ASC


asc_bp = Blueprint(
    "asc",
    __name__,
    url_prefix="/api/asc"
)


@asc_bp.post("")
def create_asc():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "asc_code",
        "asc_name",
        "pin_code"
    ]

    missing_fields = [
        field for field in required_fields
        if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "message": "Required fields are missing",
            "missing_fields": missing_fields
        }), 400

    asc_code = data["asc_code"].strip().upper()

    existing = db.session.scalar(
        select(ASC).where(ASC.asc_code == asc_code)
    )

    if existing:
        return jsonify({
            "message": "ASC code already exists",
            "asc_code": asc_code
        }), 409

    asc = ASC(
        asc_code=asc_code,
        asc_name=data["asc_name"].strip(),
        contact_person=data.get("contact_person"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        pin_code=str(data["pin_code"]).strip(),
        status=data.get("status", "Active")
    )

    db.session.add(asc)
    db.session.commit()

    return jsonify({
        "message": "ASC created successfully",
        "asc": {
            "id": asc.id,
            "asc_code": asc.asc_code,
            "asc_name": asc.asc_name,
            "contact_person": asc.contact_person,
            "phone": asc.phone,
            "email": asc.email,
            "address": asc.address,
            "city": asc.city,
            "state": asc.state,
            "pin_code": asc.pin_code,
            "status": asc.status
        }
    }), 201


@asc_bp.get("")
def get_ascs():
    ascs = db.session.scalars(
        select(ASC).order_by(ASC.id.asc())
    ).all()

    return jsonify([
        {
            "id": asc.id,
            "asc_code": asc.asc_code,
            "asc_name": asc.asc_name,
            "contact_person": asc.contact_person,
            "phone": asc.phone,
            "email": asc.email,
            "address": asc.address,
            "city": asc.city,
            "state": asc.state,
            "pin_code": asc.pin_code,
            "status": asc.status
        }
        for asc in ascs
    ]), 200


@asc_bp.get("/<int:asc_id>")
def get_asc(asc_id):
    asc = db.session.get(ASC, asc_id)

    if not asc:
        return jsonify({
            "message": "ASC not found"
        }), 404

    return jsonify({
        "id": asc.id,
        "asc_code": asc.asc_code,
        "asc_name": asc.asc_name,
        "contact_person": asc.contact_person,
        "phone": asc.phone,
        "email": asc.email,
        "address": asc.address,
        "city": asc.city,
        "state": asc.state,
        "pin_code": asc.pin_code,
        "status": asc.status
    }), 200


@asc_bp.put("/<int:asc_id>")
def update_asc(asc_id):
    asc = db.session.get(ASC, asc_id)

    if not asc:
        return jsonify({
            "message": "ASC not found"
        }), 404

    data = request.get_json(silent=True) or {}

    if "asc_code" in data:
        new_code = data["asc_code"].strip().upper()

        existing = db.session.scalar(
            select(ASC).where(
                ASC.asc_code == new_code,
                ASC.id != asc.id
            )
        )

        if existing:
            return jsonify({
                "message": "ASC code already exists",
                "asc_code": new_code
            }), 409

        asc.asc_code = new_code

    if "asc_name" in data:
        asc.asc_name = data["asc_name"].strip()

    if "contact_person" in data:
        asc.contact_person = data["contact_person"]

    if "phone" in data:
        asc.phone = data["phone"]

    if "email" in data:
        asc.email = data["email"]

    if "address" in data:
        asc.address = data["address"]

    if "city" in data:
        asc.city = data["city"]

    if "state" in data:
        asc.state = data["state"]

    if "pin_code" in data:
        asc.pin_code = str(data["pin_code"]).strip()

    if "status" in data:
        asc.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "ASC updated successfully",
        "asc_id": asc.id,
        "asc_code": asc.asc_code,
        "status": asc.status
    }), 200