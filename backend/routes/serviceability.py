from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.serviceability import Serviceability


serviceability_bp = Blueprint(
    "serviceability",
    __name__,
    url_prefix="/api/serviceability"
)


@serviceability_bp.post("")
def create_serviceability():
    data = request.get_json(silent=True) or {}

    pin_code = (data.get("pin_code") or "").strip()

    if not pin_code:
        return jsonify({
            "message": "pin_code is required"
        }), 400

    existing = db.session.scalar(
        select(Serviceability).where(
            Serviceability.pin_code == pin_code
        )
    )

    if existing:
        return jsonify({
            "message": "Serviceability record already exists for this PIN code",
            "serviceability_id": existing.id,
            "pin_code": existing.pin_code
        }), 409

    serviceability = Serviceability(
        pin_code=pin_code,
        city=data.get("city"),
        state=data.get("state"),
        serviceable=data.get("serviceable", True),
        status=data.get("status", "Active")
    )

    db.session.add(serviceability)
    db.session.commit()

    return jsonify({
        "message": "Serviceability record created successfully",
        "serviceability": {
            "id": serviceability.id,
            "pin_code": serviceability.pin_code,
            "city": serviceability.city,
            "state": serviceability.state,
            "serviceable": serviceability.serviceable,
            "status": serviceability.status
        }
    }), 201


@serviceability_bp.get("")
def get_serviceability():
    records = db.session.scalars(
        select(Serviceability)
        .order_by(Serviceability.id.asc())
    ).all()

    return jsonify([
        {
            "id": record.id,
            "pin_code": record.pin_code,
            "city": record.city,
            "state": record.state,
            "serviceable": record.serviceable,
            "status": record.status
        }
        for record in records
    ]), 200


@serviceability_bp.get("/check/<pin_code>")
def check_serviceability(pin_code):
    pin_code = pin_code.strip()

    record = db.session.scalar(
        select(Serviceability).where(
            Serviceability.pin_code == pin_code,
            Serviceability.status == "Active"
        )
    )

    if not record:
        return jsonify({
            "pin_code": pin_code,
            "serviceable": False,
            "status": "NOT_CONFIGURED",
            "message": "Serviceability is not configured for this PIN code"
        }), 200

    return jsonify({
        "pin_code": record.pin_code,
        "city": record.city,
        "state": record.state,
        "serviceable": record.serviceable,
        "status": record.status,
        "message": (
            "Service is available for this PIN code"
            if record.serviceable
            else "Service is not available for this PIN code"
        )
    }), 200