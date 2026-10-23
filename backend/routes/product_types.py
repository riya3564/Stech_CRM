from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.product_type import ProductType
from models.product_category import ProductCategory


product_types_bp = Blueprint(
    "product_types",
    __name__,
    url_prefix="/api/product-types"
)


def product_type_to_dict(product_type):
    return {
        "id": product_type.id,
        "type_code": product_type.type_code,
        "type_name": product_type.type_name,
        "category_id": product_type.category_id,
        "category_name": product_type.category.category_name,
        "description": product_type.description,
        "status": product_type.status,
        "created_at": product_type.created_at.isoformat(),
        "updated_at": product_type.updated_at.isoformat(),
    }


@product_types_bp.get("")
@jwt_required()
def get_product_types():

    product_types = db.session.scalars(
        db.select(ProductType)
        .order_by(ProductType.type_name.asc())
    ).all()

    return jsonify([
        product_type_to_dict(product_type)
        for product_type in product_types
    ]), 200


@product_types_bp.post("")
@jwt_required()
def create_product_type():

    data = request.get_json() or {}

    type_code = data.get("type_code", "").strip()
    type_name = data.get("type_name", "").strip()
    category_id = data.get("category_id")

    if not type_code:
        return jsonify({
            "message": "type_code is required."
        }), 400

    if not type_name:
        return jsonify({
            "message": "type_name is required."
        }), 400

    if not category_id:
        return jsonify({
            "message": "category_id is required."
        }), 400

    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Product category not found."
        }), 404

    existing_code = db.session.scalar(
        db.select(ProductType).where(
            ProductType.type_code == type_code
        )
    )

    if existing_code:
        return jsonify({
            "message": "Product type code already exists."
        }), 409

    product_type = ProductType(
        type_code=type_code,
        type_name=type_name,
        category_id=category_id,
        description=data.get("description"),
        status=data.get("status", "Active"),
    )

    db.session.add(product_type)
    db.session.commit()

    return jsonify({
        "message": "Product type created successfully.",
        "product_type": product_type_to_dict(product_type)
    }), 201