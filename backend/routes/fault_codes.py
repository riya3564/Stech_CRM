from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.fault_code import FaultCode
from models.product_category import ProductCategory
from models.product_type import ProductType
from models.product_model import ProductModel
from models.symptom_code import SymptomCode


fault_codes_bp = Blueprint(
    "fault_codes",
    __name__,
    url_prefix="/api/fault-codes"
)


@fault_codes_bp.get("")
@jwt_required()
def get_fault_codes():
    faults = db.session.scalars(
        db.select(FaultCode)
        .order_by(FaultCode.id)
    ).all()

    return jsonify([
        {
            "id": fault.id,
            "fault_code": fault.fault_code,
            "fault_name": fault.fault_name,
            "description": fault.description,
            "category_id": fault.category_id,
            "product_type_id": fault.product_type_id,
            "product_model_id": fault.product_model_id,
            "symptom_id": fault.symptom_id,
            "symptom_code": (
                fault.symptom.symptom_code
                if fault.symptom else None
            ),
            "status": fault.status,
        }
        for fault in faults
    ]), 200


@fault_codes_bp.post("")
@jwt_required()
def create_fault_code():
    data = request.get_json() or {}

    fault_code = data.get("fault_code", "").strip().upper()
    fault_name = data.get("fault_name", "").strip()
    description = data.get("description")
    category_id = data.get("category_id")
    product_type_id = data.get("product_type_id")
    product_model_id = data.get("product_model_id")
    symptom_id = data.get("symptom_id")

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------
    if not fault_code or not fault_name or not category_id or not symptom_id:
        return jsonify({
            "message": (
                "fault_code, fault_name, category_id "
                "and symptom_id are required."
            )
        }), 400

    # --------------------------------------------------------
    # Duplicate fault code
    # --------------------------------------------------------
    existing = db.session.scalar(
        db.select(FaultCode).where(
            FaultCode.fault_code == fault_code
        )
    )

    if existing:
        return jsonify({
            "message": "Fault code already exists."
        }), 409

    # --------------------------------------------------------
    # Validate category
    # --------------------------------------------------------
    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Invalid category_id."
        }), 400

    # --------------------------------------------------------
    # Validate product type
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Validate product model
    # --------------------------------------------------------
    product_model = None

    if product_model_id is not None:
        product_model = db.session.get(
            ProductModel,
            product_model_id
        )

        if not product_model:
            return jsonify({
                "message": "Invalid product_model_id."
            }), 400

        if product_model.category_id != category.id:
            return jsonify({
                "message": (
                    "Product model does not belong "
                    "to the selected category."
                )
            }), 400

        if (
            product_type_id is not None
            and product_model.product_type_id != product_type_id
        ):
            return jsonify({
                "message": (
                    "Product model does not belong "
                    "to the selected product type."
                )
            }), 400

    # --------------------------------------------------------
    # Validate symptom
    # --------------------------------------------------------
    symptom = db.session.get(
        SymptomCode,
        symptom_id
    )

    if not symptom:
        return jsonify({
            "message": "Invalid symptom_id."
        }), 400

    if symptom.category_id != category.id:
        return jsonify({
            "message": (
                "Symptom does not belong "
                "to the selected category."
            )
        }), 400

    if (
        product_type_id is not None
        and symptom.product_type_id is not None
        and symptom.product_type_id != product_type_id
    ):
        return jsonify({
            "message": (
                "Symptom does not belong "
                "to the selected product type."
            )
        }), 400

    # --------------------------------------------------------
    # Create fault
    # --------------------------------------------------------
    fault = FaultCode(
        fault_code=fault_code,
        fault_name=fault_name,
        description=description,
        category_id=category.id,
        product_type_id=product_type_id,
        product_model_id=product_model_id,
        symptom_id=symptom.id,
        status=data.get("status", "Active"),
    )

    db.session.add(fault)
    db.session.commit()

    return jsonify({
        "message": "Fault code created successfully.",
        "fault": {
            "id": fault.id,
            "fault_code": fault.fault_code,
            "fault_name": fault.fault_name,
            "description": fault.description,
            "category_id": fault.category_id,
            "product_type_id": fault.product_type_id,
            "product_model_id": fault.product_model_id,
            "symptom_id": fault.symptom_id,
            "symptom_code": symptom.symptom_code,
            "status": fault.status,
        }
    }), 201