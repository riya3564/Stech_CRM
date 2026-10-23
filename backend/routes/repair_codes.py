from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db

from models.repair_code import RepairCode
from models.diagnosis_code import DiagnosisCode
from models.fault_code import FaultCode
from models.product_category import ProductCategory
from models.product_type import ProductType
from models.product_model import ProductModel


repair_codes_bp = Blueprint(
    "repair_codes",
    __name__,
    url_prefix="/api/repair-codes"
)


@repair_codes_bp.get("")
@jwt_required()
def get_repair_codes():

    repairs = db.session.scalars(
        db.select(RepairCode)
        .order_by(RepairCode.id)
    ).all()

    return jsonify([
        {
            "id": repair.id,
            "repair_code": repair.repair_code,
            "repair_name": repair.repair_name,
            "description": repair.description,

            "category_id": repair.category_id,
            "product_type_id": repair.product_type_id,
            "product_model_id": repair.product_model_id,

            "fault_id": repair.fault_id,
            "fault_code": (
                repair.fault.fault_code
                if repair.fault
                else None
            ),

            "diagnosis_id": repair.diagnosis_id,
            "diagnosis_code": (
                repair.diagnosis.diagnosis_code
                if repair.diagnosis
                else None
            ),

            "status": repair.status,
        }
        for repair in repairs
    ]), 200


@repair_codes_bp.post("")
@jwt_required()
def create_repair_code():

    data = request.get_json() or {}

    repair_code = data.get(
        "repair_code",
        ""
    ).strip().upper()

    repair_name = data.get(
        "repair_name",
        ""
    ).strip()

    description = data.get(
        "description"
    )

    category_id = data.get(
        "category_id"
    )

    product_type_id = data.get(
        "product_type_id"
    )

    product_model_id = data.get(
        "product_model_id"
    )

    fault_id = data.get(
        "fault_id"
    )

    diagnosis_id = data.get(
        "diagnosis_id"
    )

    # ---------------------------------------------------------
    # REQUIRED FIELDS
    # ---------------------------------------------------------

    if (
        not repair_code
        or not repair_name
        or not category_id
        or not fault_id
        or not diagnosis_id
    ):
        return jsonify({
            "message": (
                "repair_code, repair_name, category_id, "
                "fault_id and diagnosis_id are required."
            )
        }), 400

    # ---------------------------------------------------------
    # DUPLICATE CHECK
    # ---------------------------------------------------------

    existing = db.session.scalar(
        db.select(RepairCode).where(
            RepairCode.repair_code == repair_code
        )
    )

    if existing:
        return jsonify({
            "message": "Repair code already exists."
        }), 409

    # ---------------------------------------------------------
    # CATEGORY VALIDATION
    # ---------------------------------------------------------

    category = db.session.get(
        ProductCategory,
        category_id
    )

    if not category:
        return jsonify({
            "message": "Invalid category_id."
        }), 400

    # ---------------------------------------------------------
    # FAULT VALIDATION
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # DIAGNOSIS VALIDATION
    # ---------------------------------------------------------

    diagnosis = db.session.get(
        DiagnosisCode,
        diagnosis_id
    )

    if not diagnosis:
        return jsonify({
            "message": "Invalid diagnosis_id."
        }), 400

    if diagnosis.category_id != category.id:
        return jsonify({
            "message": (
                "Diagnosis does not belong "
                "to the selected category."
            )
        }), 400

    # Diagnosis MUST belong to selected Fault
    if diagnosis.fault_id != fault.id:
        return jsonify({
            "message": (
                "Diagnosis does not belong "
                "to the selected fault."
            )
        }), 400

    # ---------------------------------------------------------
    # PRODUCT TYPE VALIDATION
    # ---------------------------------------------------------

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

        if (
            diagnosis.product_type_id is not None
            and diagnosis.product_type_id != product_type_id
        ):
            return jsonify({
                "message": (
                    "Diagnosis does not belong "
                    "to the selected product type."
                )
            }), 400

    # ---------------------------------------------------------
    # PRODUCT MODEL VALIDATION
    # ---------------------------------------------------------

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
            and product_model.product_type_id
            != product_type_id
        ):
            return jsonify({
                "message": (
                    "Product model does not belong "
                    "to the selected product type."
                )
            }), 400

        if (
            fault.product_model_id is not None
            and fault.product_model_id
            != product_model_id
        ):
            return jsonify({
                "message": (
                    "Fault does not belong "
                    "to the selected product model."
                )
            }), 400

        if (
            diagnosis.product_model_id is not None
            and diagnosis.product_model_id
            != product_model_id
        ):
            return jsonify({
                "message": (
                    "Diagnosis does not belong "
                    "to the selected product model."
                )
            }), 400

    # ---------------------------------------------------------
    # CREATE REPAIR
    # ---------------------------------------------------------

    repair = RepairCode(
        repair_code=repair_code,
        repair_name=repair_name,
        description=description,

        category_id=category.id,

        product_type_id=product_type_id,

        product_model_id=product_model_id,

        fault_id=fault.id,

        diagnosis_id=diagnosis.id,

        status=data.get(
            "status",
            "Active"
        ),
    )

    db.session.add(repair)
    db.session.commit()

    return jsonify({
        "message": (
            "Repair code created successfully."
        ),

        "repair": {
            "id": repair.id,
            "repair_code": repair.repair_code,
            "repair_name": repair.repair_name,
            "description": repair.description,

            "category_id": repair.category_id,
            "product_type_id": repair.product_type_id,
            "product_model_id": repair.product_model_id,

            "fault_id": repair.fault_id,
            "fault_code": fault.fault_code,

            "diagnosis_id": repair.diagnosis_id,
            "diagnosis_code": diagnosis.diagnosis_code,

            "status": repair.status,
        }
    }), 201