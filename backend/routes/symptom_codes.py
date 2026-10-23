from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.symptom_code import SymptomCode
from models.product_category import ProductCategory
from models.product_type import ProductType
from models.product_model import ProductModel


symptom_codes_bp = Blueprint(
    "symptom_codes",
    __name__,
    url_prefix="/api/symptom-codes"
)


def symptom_to_dict(symptom):
    return {
        "id": symptom.id,
        "symptom_code": symptom.symptom_code,
        "symptom_name": symptom.symptom_name,
        "description": symptom.description,
        "category_id": symptom.category_id,
        "category_name": symptom.category.category_name,
        "product_type_id": symptom.product_type_id,
        "product_type_name": (
            symptom.product_type.type_name
            if symptom.product_type
            else None
        ),
        "product_model_id": symptom.product_model_id,
        "model_number": (
            symptom.product_model.model_number
            if symptom.product_model
            else None
        ),
        "status": symptom.status,
        "created_at": symptom.created_at.isoformat(),
        "updated_at": symptom.updated_at.isoformat(),
    }


@symptom_codes_bp.get("")
@jwt_required()
def get_symptom_codes():

    symptoms = db.session.scalars(
        db.select(SymptomCode)
        .order_by(SymptomCode.symptom_code.asc())
    ).all()

    return jsonify([
        symptom_to_dict(symptom)
        for symptom in symptoms
    ]), 200


@symptom_codes_bp.post("")
@jwt_required()
def create_symptom_code():

    data = request.get_json() or {}

    symptom_code = data.get("symptom_code", "").strip()
    symptom_name = data.get("symptom_name", "").strip()
    category_id = data.get("category_id")
    product_type_id = data.get("product_type_id")
    product_model_id = data.get("product_model_id")

    if not symptom_code:
        return jsonify({
            "message": "symptom_code is required."
        }), 400

    if not symptom_name:
        return jsonify({
            "message": "symptom_name is required."
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

    product_type = None

    if product_type_id:

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

    product_model = None

    if product_model_id:

        product_model = db.session.get(
            ProductModel,
            product_model_id
        )

        if not product_model:
            return jsonify({
                "message": "Product model not found."
            }), 404

        if product_model.category_id != category_id:
            return jsonify({
                "message": "Product model does not belong to selected category."
            }), 400

        if product_type_id and product_model.product_type_id != product_type_id:
            return jsonify({
                "message": "Product model does not belong to selected product type."
            }), 400

    existing = db.session.scalar(
        db.select(SymptomCode).where(
            SymptomCode.symptom_code == symptom_code
        )
    )

    if existing:
        return jsonify({
            "message": "Symptom code already exists."
        }), 409

    symptom = SymptomCode(
        symptom_code=symptom_code,
        symptom_name=symptom_name,
        description=data.get("description"),
        category_id=category_id,
        product_type_id=product_type_id,
        product_model_id=product_model_id,
        status=data.get("status", "Active"),
    )

    db.session.add(symptom)
    db.session.commit()

    return jsonify({
        "message": "Symptom code created successfully.",
        "symptom": symptom_to_dict(symptom)
    }), 201