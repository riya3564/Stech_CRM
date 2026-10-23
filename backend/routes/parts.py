from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.part import Part
from models.brand import Brand
from models.product_category import ProductCategory
from models.product_type import ProductType


parts_bp = Blueprint(
    "parts",
    __name__,
    url_prefix="/api/parts"
)


@parts_bp.get("")
@jwt_required()
def get_parts():
    parts = (
        Part.query
        .order_by(Part.id.asc())
        .all()
    )

    return jsonify([
        {
            "id": part.id,
            "part_code": part.part_code,
            "part_name": part.part_name,
            "description": part.description,
            "brand_id": part.brand_id,
            "brand_name": part.brand.brand_name if part.brand else None,
            "category_id": part.category_id,
            "category_name": (
                part.category.category_name
                if part.category else None
            ),
            "product_type_id": part.product_type_id,
            "product_type_name": (
                part.product_type.type_name
                if part.product_type else None
            ),
            "status": part.status,
        }
        for part in parts
    ]), 200


@parts_bp.post("")
@jwt_required()
def create_part():
    data = request.get_json() or {}

    part_code = data.get("part_code", "").strip().upper()
    part_name = data.get("part_name", "").strip()
    description = data.get("description")
    brand_id = data.get("brand_id")
    category_id = data.get("category_id")
    product_type_id = data.get("product_type_id")
    status = data.get("status", "Active").strip()

    if not part_code:
        return jsonify({
            "message": "Part code is required."
        }), 400

    if not part_name:
        return jsonify({
            "message": "Part name is required."
        }), 400

    if not category_id:
        return jsonify({
            "message": "Category ID is required."
        }), 400

    existing = Part.query.filter_by(
        part_code=part_code
    ).first()

    if existing:
        return jsonify({
            "message": "Part code already exists."
        }), 409

    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Invalid category_id."
        }), 400

    brand = None

    if brand_id is not None:
        brand = db.session.get(
            Brand,
            brand_id
        )

        if not brand:
            return jsonify({
                "message": "Invalid brand_id."
            }), 400

    product_type = None

    if product_type_id is not None:
        product_type = db.session.get(
            ProductType,
            product_type_id
        )

        if not product_type:
            return jsonify({
                "message": "Invalid product_type_id."
            }), 400

        if product_type.category_id != category.id:
            return jsonify({
                "message": (
                    "Product type does not belong "
                    "to the selected category."
                )
            }), 400

    part = Part(
        part_code=part_code,
        part_name=part_name,
        description=description,
        brand_id=brand.id if brand else None,
        category_id=category.id,
        product_type_id=(
            product_type.id
            if product_type else None
        ),
        status=status
    )

    db.session.add(part)
    db.session.commit()

    return jsonify({
        "message": "Part created successfully.",
        "part": {
            "id": part.id,
            "part_code": part.part_code,
            "part_name": part.part_name,
            "description": part.description,
            "brand_id": part.brand_id,
            "category_id": part.category_id,
            "product_type_id": part.product_type_id,
            "status": part.status
        }
    }), 201