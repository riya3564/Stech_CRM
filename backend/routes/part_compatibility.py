from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.part_compatibility import PartCompatibility
from models.product_model import ProductModel
from models.diagnosis_code import DiagnosisCode
from models.repair_code import RepairCode
from models.part import Part


part_compatibility_bp = Blueprint(
    "part_compatibility",
    __name__,
    url_prefix="/api/part-compatibility"
)


@part_compatibility_bp.get("")
@jwt_required()
def get_part_compatibilities():

    records = (
        PartCompatibility.query
        .order_by(PartCompatibility.id.asc())
        .all()
    )

    return jsonify([
        {
            "id": record.id,

            "product_model_id": record.product_model_id,
            "product_model": (
                record.product_model.model_number
                if record.product_model
                else None
            ),

            "diagnosis_id": record.diagnosis_id,
            "diagnosis_code": (
                record.diagnosis.diagnosis_code
                if record.diagnosis
                else None
            ),

            "repair_id": record.repair_id,
            "repair_code": (
                record.repair.repair_code
                if record.repair
                else None
            ),

            "part_id": record.part_id,
            "part_code": (
                record.part.part_code
                if record.part
                else None
            ),
            "part_name": (
                record.part.part_name
                if record.part
                else None
            ),

            "priority": record.priority,
            "is_active": record.is_active,
            "notes": record.notes
        }
        for record in records
    ]), 200


@part_compatibility_bp.post("")
@jwt_required()
def create_part_compatibility():

    data = request.get_json() or {}

    product_model_id = data.get("product_model_id")
    diagnosis_id = data.get("diagnosis_id")
    repair_id = data.get("repair_id")
    part_id = data.get("part_id")
    priority = data.get("priority", 1)
    is_active = data.get("is_active", True)
    notes = data.get("notes")

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    if diagnosis_id is None:
        return jsonify({
            "message": "diagnosis_id is required."
        }), 400

    if repair_id is None:
        return jsonify({
            "message": "repair_id is required."
        }), 400

    if part_id is None:
        return jsonify({
            "message": "part_id is required."
        }), 400

    # ---------------------------------------------------------
    # Fetch master records
    # ---------------------------------------------------------

    diagnosis = db.session.get(
        DiagnosisCode,
        diagnosis_id
    )

    if not diagnosis:
        return jsonify({
            "message": "Invalid diagnosis_id."
        }), 400

    repair = db.session.get(
        RepairCode,
        repair_id
    )

    if not repair:
        return jsonify({
            "message": "Invalid repair_id."
        }), 400

    part = db.session.get(
        Part,
        part_id
    )

    if not part:
        return jsonify({
            "message": "Invalid part_id."
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

    # ---------------------------------------------------------
    # Diagnosis → Repair validation
    # ---------------------------------------------------------

    if repair.diagnosis_id != diagnosis.id:
        return jsonify({
            "message": (
                "Selected repair does not belong "
                "to the selected diagnosis."
            )
        }), 400

    # ---------------------------------------------------------
    # Diagnosis → Fault consistency
    # ---------------------------------------------------------

    if repair.fault_id != diagnosis.fault_id:
        return jsonify({
            "message": (
                "Repair fault does not match "
                "diagnosis fault."
            )
        }), 400

    # ---------------------------------------------------------
    # Category consistency
    # ---------------------------------------------------------

    if part.category_id != diagnosis.category_id:
        return jsonify({
            "message": (
                "Part category does not match "
                "diagnosis category."
            )
        }), 400

    # ---------------------------------------------------------
    # Product type consistency
    # ---------------------------------------------------------

    if (
        part.product_type_id is not None
        and diagnosis.product_type_id is not None
        and part.product_type_id != diagnosis.product_type_id
    ):
        return jsonify({
            "message": (
                "Part product type does not match "
                "diagnosis product type."
            )
        }), 400

    # ---------------------------------------------------------
    # Product model consistency
    # ---------------------------------------------------------

    if product_model:

        if diagnosis.product_model_id is not None:
            if diagnosis.product_model_id != product_model.id:
                return jsonify({
                    "message": (
                        "Product model does not match "
                        "diagnosis model."
                    )
                }), 400

        if part.category_id != product_model.category_id:
            return jsonify({
                "message": (
                    "Part category does not match "
                    "product model category."
                )
            }), 400

        if (
            part.product_type_id is not None
            and part.product_type_id != product_model.product_type_id
        ):
            return jsonify({
                "message": (
                    "Part product type does not match "
                    "product model type."
                )
            }), 400

    # ---------------------------------------------------------
    # Duplicate compatibility check
    # ---------------------------------------------------------

    existing_query = PartCompatibility.query.filter_by(
        diagnosis_id=diagnosis.id,
        repair_id=repair.id,
        part_id=part.id
    )

    if product_model:
        existing_query = existing_query.filter_by(
            product_model_id=product_model.id
        )
    else:
        existing_query = existing_query.filter(
            PartCompatibility.product_model_id.is_(None)
        )

    existing = existing_query.first()

    if existing:
        return jsonify({
            "message": (
                "This part compatibility mapping "
                "already exists."
            )
        }), 409

    # ---------------------------------------------------------
    # Create compatibility record
    # ---------------------------------------------------------

    compatibility = PartCompatibility(
        product_model_id=(
            product_model.id
            if product_model
            else None
        ),
        diagnosis_id=diagnosis.id,
        repair_id=repair.id,
        part_id=part.id,
        priority=priority,
        is_active=is_active,
        notes=notes
    )

    db.session.add(compatibility)
    db.session.commit()

    return jsonify({
        "message": (
            "Part compatibility created successfully."
        ),
        "compatibility": {
            "id": compatibility.id,
            "product_model_id": compatibility.product_model_id,
            "diagnosis_id": compatibility.diagnosis_id,
            "repair_id": compatibility.repair_id,
            "part_id": compatibility.part_id,
            "priority": compatibility.priority,
            "is_active": compatibility.is_active,
            "notes": compatibility.notes
        }
    }), 201