from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.diagnosis_code import DiagnosisCode
from models.fault_code import FaultCode
from models.product_category import ProductCategory
from models.product_type import ProductType
from models.product_model import ProductModel


diagnosis_codes_bp = Blueprint(
    "diagnosis_codes",
    __name__,
    url_prefix="/api/diagnosis-codes"
)


@diagnosis_codes_bp.get("")
@jwt_required()
def get_diagnosis_codes():
    diagnoses = db.session.scalars(
        db.select(DiagnosisCode)
        .order_by(DiagnosisCode.id)
    ).all()

    return jsonify([
        {
            "id": diagnosis.id,
            "diagnosis_code": diagnosis.diagnosis_code,
            "diagnosis_name": diagnosis.diagnosis_name,
            "description": diagnosis.description,
            "category_id": diagnosis.category_id,
            "product_type_id": diagnosis.product_type_id,
            "product_model_id": diagnosis.product_model_id,
            "fault_id": diagnosis.fault_id,
            "fault_code": (
                diagnosis.fault.fault_code
                if diagnosis.fault else None
            ),
            "status": diagnosis.status,
        }
        for diagnosis in diagnoses
    ]), 200


@diagnosis_codes_bp.post("")
@jwt_required()
def create_diagnosis_code():
    data = request.get_json() or {}

    diagnosis_code = data.get(
        "diagnosis_code", ""
    ).strip().upper()

    diagnosis_name = data.get(
        "diagnosis_name", ""
    ).strip()

    description = data.get("description")

    category_id = data.get("category_id")
    product_type_id = data.get("product_type_id")
    product_model_id = data.get("product_model_id")
    fault_id = data.get("fault_id")

    if (
        not diagnosis_code
        or not diagnosis_name
        or not category_id
        or not fault_id
    ):
        return jsonify({
            "message": (
                "diagnosis_code, diagnosis_name, "
                "category_id and fault_id are required."
            )
        }), 400

    existing = db.session.scalar(
        db.select(DiagnosisCode).where(
            DiagnosisCode.diagnosis_code == diagnosis_code
        )
    )

    if existing:
        return jsonify({
            "message": "Diagnosis code already exists."
        }), 409

    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Invalid category_id."
        }), 400

    fault = db.session.get(
        FaultCode,
        fault_id
    )

    if not fault:
        return jsonify({
            "message": "Invalid fault_id."
        }), 400

    if fault.category_id != category.id:
        return jsonify({
            "message": (
                "Fault does not belong "
                "to the selected category."
            )
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

        if (
            fault.product_type_id is not None
            and fault.product_type_id != product_type_id
        ):
            return jsonify({
                "message": (
                    "Fault does not belong "
                    "to the selected product type."
                )
            }), 400

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

    diagnosis = DiagnosisCode(
        diagnosis_code=diagnosis_code,
        diagnosis_name=diagnosis_name,
        description=description,
        category_id=category.id,
        product_type_id=product_type_id,
        product_model_id=product_model_id,
        fault_id=fault.id,
        status=data.get("status", "Active"),
    )

    db.session.add(diagnosis)
    db.session.commit()

    return jsonify({
        "message": "Diagnosis code created successfully.",
        "diagnosis": {
            "id": diagnosis.id,
            "diagnosis_code": diagnosis.diagnosis_code,
            "diagnosis_name": diagnosis.diagnosis_name,
            "description": diagnosis.description,
            "category_id": diagnosis.category_id,
            "product_type_id": diagnosis.product_type_id,
            "product_model_id": diagnosis.product_model_id,
            "fault_id": diagnosis.fault_id,
            "fault_code": fault.fault_code,
            "status": diagnosis.status,
        }
    }), 201