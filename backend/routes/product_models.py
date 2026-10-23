from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.product_model import ProductModel
from models.brand import Brand
from models.product_category import ProductCategory
from models.product_type import ProductType


product_models_bp = Blueprint(
    "product_models",
    __name__,
    url_prefix="/api/product-models"
)


def product_model_to_dict(product_model):
    return {
        "id": product_model.id,
        "model_code": product_model.model_code,
        "model_number": product_model.model_number,
        "model_name": product_model.model_name,
        "brand_id": product_model.brand_id,
        "brand_name": product_model.brand.brand_name,
        "category_id": product_model.category_id,
        "category_name": product_model.category.category_name,
        "product_type_id": product_model.product_type_id,
        "product_type_name": product_model.product_type.type_name,
        "description": product_model.description,
        "status": product_model.status,
        "created_at": product_model.created_at.isoformat(),
        "updated_at": product_model.updated_at.isoformat(),
    }


@product_models_bp.get("")
@jwt_required()
def get_product_models():

    product_models = db.session.scalars(
        db.select(ProductModel)
        .order_by(ProductModel.model_number.asc())
    ).all()

    return jsonify([
        product_model_to_dict(product_model)
        for product_model in product_models
    ]), 200


@product_models_bp.post("")
@jwt_required()
def create_product_model():

    data = request.get_json() or {}

    model_code = data.get("model_code", "").strip()
    model_number = data.get("model_number", "").strip()
    model_name = data.get("model_name")
    brand_id = data.get("brand_id")
    category_id = data.get("category_id")
    product_type_id = data.get("product_type_id")

    if not model_code:
        return jsonify({
            "message": "model_code is required."
        }), 400

    if not model_number:
        return jsonify({
            "message": "model_number is required."
        }), 400

    if not brand_id:
        return jsonify({
            "message": "brand_id is required."
        }), 400

    if not category_id:
        return jsonify({
            "message": "category_id is required."
        }), 400

    if not product_type_id:
        return jsonify({
            "message": "product_type_id is required."
        }), 400

    brand = db.session.get(
        Brand,
        brand_id
    )

    if not brand:
        return jsonify({
            "message": "Brand not found."
        }), 404

    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Product category not found."
        }), 404

    product_type = db.session.get(
        ProductType,
        product_type_id
    )

    if not product_type:
        return jsonify({
            "message": "Product type not found."
        }), 404

    if product_type.category_id != category_id:
        return jsonify({
            "message": "Product type does not belong to selected category."
        }), 400

    existing_code = db.session.scalar(
        db.select(ProductModel).where(
            ProductModel.model_code == model_code
        )
    )

    if existing_code:
        return jsonify({
            "message": "Model code already exists."
        }), 409

    product_model = ProductModel(
        model_code=model_code,
        model_number=model_number,
        model_name=model_name,
        brand_id=brand_id,
        category_id=category_id,
        product_type_id=product_type_id,
        description=data.get("description"),
        status=data.get("status", "Active"),
    )

    db.session.add(product_model)
    db.session.commit()

    return jsonify({
        "message": "Product model created successfully.",
        "product_model": product_model_to_dict(product_model)
    }), 201