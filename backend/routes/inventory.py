from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.inventory import Inventory
from models.part import Part


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory"
)


@inventory_bp.post("")
def create_inventory():
    data = request.get_json(silent=True) or {}

    part_id = data.get("part_id")

    if not part_id:
        return jsonify({
            "message": "part_id is required"
        }), 400

    part = db.session.get(Part, part_id)

    if not part:
        return jsonify({
            "message": "Part not found"
        }), 404

    existing = db.session.scalar(
        select(Inventory).where(
            Inventory.part_id == part_id
        )
    )

    if existing:
        return jsonify({
            "message": "Inventory already exists for this part",
            "inventory_id": existing.id
        }), 409

    try:
        available_quantity = int(
            data.get("available_quantity", 0)
        )

        reserved_quantity = int(
            data.get("reserved_quantity", 0)
        )

        reorder_level = int(
            data.get("reorder_level", 0)
        )

    except (TypeError, ValueError):
        return jsonify({
            "message": "Quantity and reorder_level must be integers"
        }), 400

    if available_quantity < 0:
        return jsonify({
            "message": "available_quantity cannot be negative"
        }), 400

    if reserved_quantity < 0:
        return jsonify({
            "message": "reserved_quantity cannot be negative"
        }), 400

    if reorder_level < 0:
        return jsonify({
            "message": "reorder_level cannot be negative"
        }), 400

    inventory = Inventory(
        part_id=part_id,
        warehouse_name=data.get("warehouse_name"),
        available_quantity=available_quantity,
        reserved_quantity=reserved_quantity,
        reorder_level=reorder_level,
        status=data.get("status", "Active")
    )

    db.session.add(inventory)
    db.session.commit()

    return jsonify({
        "message": "Inventory created successfully",
        "inventory": {
            "id": inventory.id,
            "part_id": inventory.part_id,
            "part_code": part.part_code,
            "part_name": part.part_name,
            "warehouse_name": inventory.warehouse_name,
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "reorder_level": inventory.reorder_level,
            "status": inventory.status
        }
    }), 201


@inventory_bp.get("")
def get_inventory():

    records = db.session.scalars(
        select(Inventory).order_by(
            Inventory.id.desc()
        )
    ).all()

    result = []

    for inventory in records:

        part = db.session.get(
            Part,
            inventory.part_id
        )

        result.append({
            "id": inventory.id,
            "part_id": inventory.part_id,
            "part_code": part.part_code if part else None,
            "part_name": part.part_name if part else None,
            "warehouse_name": inventory.warehouse_name,
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "reorder_level": inventory.reorder_level,
            "status": inventory.status
        })

    return jsonify(result), 200


@inventory_bp.get("/<int:inventory_id>")
def get_inventory_record(inventory_id):

    inventory = db.session.get(
        Inventory,
        inventory_id
    )

    if not inventory:
        return jsonify({
            "message": "Inventory record not found"
        }), 404

    part = db.session.get(
        Part,
        inventory.part_id
    )

    return jsonify({
        "id": inventory.id,
        "part_id": inventory.part_id,
        "part_code": part.part_code if part else None,
        "part_name": part.part_name if part else None,
        "warehouse_name": inventory.warehouse_name,
        "available_quantity": inventory.available_quantity,
        "reserved_quantity": inventory.reserved_quantity,
        "reorder_level": inventory.reorder_level,
        "status": inventory.status
    }), 200