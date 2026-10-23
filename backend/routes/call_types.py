from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.call_type import CallType


call_types_bp = Blueprint(
    "call_types",
    __name__,
    url_prefix="/api/call-types"
)


@call_types_bp.get("")
def get_call_types():
    call_types = db.session.scalars(
        select(CallType)
        .order_by(CallType.id.asc())
    ).all()

    return jsonify({
        "value": [
            {
                "id": call_type.id,
                "call_type_code": call_type.call_type_code,
                "call_type_name": call_type.call_type_name,
                "description": call_type.description,
                "status": call_type.status,
                "created_at": (
                    call_type.created_at.isoformat()
                    if call_type.created_at
                    else None
                ),
                "updated_at": (
                    call_type.updated_at.isoformat()
                    if call_type.updated_at
                    else None
                )
            }
            for call_type in call_types
        ],
        "Count": len(call_types)
    })


@call_types_bp.get("/<int:call_type_id>")
def get_call_type(call_type_id):
    call_type = db.session.get(CallType, call_type_id)

    if not call_type:
        return jsonify({
            "message": "Call type not found"
        }), 404

    return jsonify({
        "id": call_type.id,
        "call_type_code": call_type.call_type_code,
        "call_type_name": call_type.call_type_name,
        "description": call_type.description,
        "status": call_type.status,
        "created_at": (
            call_type.created_at.isoformat()
            if call_type.created_at
            else None
        ),
        "updated_at": (
            call_type.updated_at.isoformat()
            if call_type.updated_at
            else None
        )
    })


@call_types_bp.post("")
def create_call_type():
    data = request.get_json(silent=True) or {}

    call_type_code = (data.get("call_type_code") or "").strip()
    call_type_name = (data.get("call_type_name") or "").strip()

    if not call_type_code or not call_type_name:
        return jsonify({
            "message": "call_type_code and call_type_name are required"
        }), 400

    existing_code = db.session.scalar(
        select(CallType).where(
            CallType.call_type_code == call_type_code
        )
    )

    if existing_code:
        return jsonify({
            "message": "Call type code already exists"
        }), 409

    existing_name = db.session.scalar(
        select(CallType).where(
            CallType.call_type_name == call_type_name
        )
    )

    if existing_name:
        return jsonify({
            "message": "Call type name already exists"
        }), 409

    call_type = CallType(
        call_type_code=call_type_code,
        call_type_name=call_type_name,
        description=data.get("description"),
        status=data.get("status", "Active")
    )

    db.session.add(call_type)
    db.session.commit()

    return jsonify({
        "message": "Call type created successfully",
        "call_type": {
            "id": call_type.id,
            "call_type_code": call_type.call_type_code,
            "call_type_name": call_type.call_type_name,
            "description": call_type.description,
            "status": call_type.status
        }
    }), 201