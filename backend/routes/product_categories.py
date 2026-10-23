from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.product_category import ProductCategory


product_categories_bp = Blueprint(
    "product_categories",
    __name__,
    url_prefix="/api/product-categories"
)


def category_to_dict(category):
    return {
        "id": category.id,
        "category_code": category.category_code,
        "category_name": category.category_name,
        "description": category.description,
        "status": category.status,
        "created_at": category.created_at.isoformat(),
        "updated_at": category.updated_at.isoformat(),
    }


@product_categories_bp.get("")
@jwt_required()
def get_categories():

    categories = db.session.scalars(
        db.select(ProductCategory)
        .order_by(ProductCategory.category_name.asc())
    ).all()

    return jsonify([
        category_to_dict(category)
        for category in categories
    ]), 200


@product_categories_bp.post("")
@jwt_required()
def create_category():

    data = request.get_json() or {}

    category_code = data.get("category_code", "").strip()
    category_name = data.get("category_name", "").strip()

    if not category_code:
        return jsonify({
            "message": "category_code is required."
        }), 400

    if not category_name:
        return jsonify({
            "message": "category_name is required."
        }), 400

    existing_code = db.session.scalar(
        db.select(ProductCategory).where(
            ProductCategory.category_code == category_code
        )
    )

    if existing_code:
        return jsonify({
            "message": "Category code already exists."
        }), 409

    existing_name = db.session.scalar(
        db.select(ProductCategory).where(
            ProductCategory.category_name == category_name
        )
    )

    if existing_name:
        return jsonify({
            "message": "Category name already exists."
        }), 409

    category = ProductCategory(
        category_code=category_code,
        category_name=category_name,
        description=data.get("description"),
        status=data.get("status", "Active"),
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "message": "Product category created successfully.",
        "category": category_to_dict(category)
    }), 201