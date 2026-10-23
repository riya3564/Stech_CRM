from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.diagnosis import Diagnosis
from models.service_call import ServiceCall
from models.engineer_visit import EngineerVisit
from models.symptom_code import SymptomCode
from models.fault_code import FaultCode
from models.diagnosis_code import DiagnosisCode


diagnoses_bp = Blueprint(
    "diagnoses",
    __name__,
    url_prefix="/api/diagnoses"
)


@diagnoses_bp.post("")
def create_diagnosis():
    data = request.get_json(silent=True) or {}

    service_call_id = data.get("service_call_id")
    visit_id = data.get("visit_id")
    diagnosis_code_id = data.get("diagnosis_code_id")

    if not service_call_id:
        return jsonify({
            "message": "service_call_id is required"
        }), 400

    if not visit_id:
        return jsonify({
            "message": "visit_id is required"
        }), 400

    if not diagnosis_code_id:
        return jsonify({
            "message": "diagnosis_code_id is required"
        }), 400

    service_call = db.session.get(
        ServiceCall,
        service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service call not found"
        }), 404

    visit = db.session.get(
        EngineerVisit,
        visit_id
    )

    if not visit:
        return jsonify({
            "message": "Engineer visit not found"
        }), 404

    if visit.service_call_id != service_call_id:
        return jsonify({
            "message": "Engineer visit does not belong to this service call"
        }), 400

    diagnosis_code = db.session.get(
        DiagnosisCode,
        diagnosis_code_id
    )

    if not diagnosis_code:
        return jsonify({
            "message": "Diagnosis code not found"
        }), 404

    symptom_code_id = data.get("symptom_code_id")

    if symptom_code_id:
        symptom = db.session.get(
            SymptomCode,
            symptom_code_id
        )

        if not symptom:
            return jsonify({
                "message": "Symptom code not found"
            }), 404

    fault_code_id = data.get("fault_code_id")

    if fault_code_id:
        fault = db.session.get(
            FaultCode,
            fault_code_id
        )

        if not fault:
            return jsonify({
                "message": "Fault code not found"
            }), 404

    last_diagnosis = db.session.scalar(
        select(Diagnosis)
        .order_by(Diagnosis.id.desc())
        .limit(1)
    )

    next_number = (
        1
        if not last_diagnosis
        else last_diagnosis.id + 1
    )

    diagnosis_number = f"DIAG-{next_number:04d}"

    diagnosis = Diagnosis(
        diagnosis_number=diagnosis_number,
        service_call_id=service_call_id,
        visit_id=visit_id,
        symptom_code_id=symptom_code_id,
        fault_code_id=fault_code_id,
        diagnosis_code_id=diagnosis_code_id,
        observation=data.get("observation"),
        actual_fault=data.get("actual_fault"),
        root_cause=data.get("root_cause"),
        diagnostic_actions=data.get(
            "diagnostic_actions"
        ),
        customer_issue=data.get(
            "customer_issue"
        ),
        product_issue=data.get(
            "product_issue"
        ),
        part_required=data.get(
            "part_required",
            False
        ),
        evidence=data.get("evidence"),
        status=data.get(
            "status",
            "Diagnosed"
        ),
        remarks=data.get("remarks")
    )

    db.session.add(diagnosis)

    service_call.status = "Diagnosed"

    visit.status = "Completed"
    visit.outcome = "Diagnosis Completed"

    db.session.commit()

    return jsonify({
        "message": "Diagnosis created successfully",
        "diagnosis": {
            "id": diagnosis.id,
            "diagnosis_number": diagnosis.diagnosis_number,
            "service_call_id": diagnosis.service_call_id,
            "visit_id": diagnosis.visit_id,
            "symptom_code_id": diagnosis.symptom_code_id,
            "fault_code_id": diagnosis.fault_code_id,
            "diagnosis_code_id": diagnosis.diagnosis_code_id,
            "observation": diagnosis.observation,
            "actual_fault": diagnosis.actual_fault,
            "root_cause": diagnosis.root_cause,
            "part_required": diagnosis.part_required,
            "status": diagnosis.status
        },
        "service_call": {
            "call_id": service_call.call_id,
            "status": service_call.status
        }
    }), 201


@diagnoses_bp.get("")
def get_diagnoses():
    diagnoses = db.session.scalars(
        select(Diagnosis)
        .order_by(Diagnosis.id.desc())
    ).all()

    result = []

    for diagnosis in diagnoses:
        service_call = db.session.get(
            ServiceCall,
            diagnosis.service_call_id
        )

        result.append({
            "id": diagnosis.id,
            "diagnosis_number": diagnosis.diagnosis_number,
            "service_call_id": diagnosis.service_call_id,
            "call_id": (
                service_call.call_id
                if service_call
                else None
            ),
            "visit_id": diagnosis.visit_id,
            "symptom_code_id": diagnosis.symptom_code_id,
            "fault_code_id": diagnosis.fault_code_id,
            "diagnosis_code_id": diagnosis.diagnosis_code_id,
            "observation": diagnosis.observation,
            "actual_fault": diagnosis.actual_fault,
            "root_cause": diagnosis.root_cause,
            "diagnostic_actions": diagnosis.diagnostic_actions,
            "customer_issue": diagnosis.customer_issue,
            "product_issue": diagnosis.product_issue,
            "part_required": diagnosis.part_required,
            "evidence": diagnosis.evidence,
            "status": diagnosis.status,
            "remarks": diagnosis.remarks
        })

    return jsonify(result), 200


@diagnoses_bp.get("/<int:diagnosis_id>")
def get_diagnosis(diagnosis_id):
    diagnosis = db.session.get(
        Diagnosis,
        diagnosis_id
    )

    if not diagnosis:
        return jsonify({
            "message": "Diagnosis not found"
        }), 404

    return jsonify({
        "id": diagnosis.id,
        "diagnosis_number": diagnosis.diagnosis_number,
        "service_call_id": diagnosis.service_call_id,
        "visit_id": diagnosis.visit_id,
        "symptom_code_id": diagnosis.symptom_code_id,
        "fault_code_id": diagnosis.fault_code_id,
        "diagnosis_code_id": diagnosis.diagnosis_code_id,
        "observation": diagnosis.observation,
        "actual_fault": diagnosis.actual_fault,
        "root_cause": diagnosis.root_cause,
        "diagnostic_actions": diagnosis.diagnostic_actions,
        "customer_issue": diagnosis.customer_issue,
        "product_issue": diagnosis.product_issue,
        "part_required": diagnosis.part_required,
        "evidence": diagnosis.evidence,
        "status": diagnosis.status,
        "remarks": diagnosis.remarks
    }), 200


@diagnoses_bp.put("/<int:diagnosis_id>")
def update_diagnosis(diagnosis_id):
    diagnosis = db.session.get(
        Diagnosis,
        diagnosis_id
    )

    if not diagnosis:
        return jsonify({
            "message": "Diagnosis not found"
        }), 404

    data = request.get_json(silent=True) or {}

    allowed_fields = [
        "observation",
        "actual_fault",
        "root_cause",
        "diagnostic_actions",
        "customer_issue",
        "product_issue",
        "part_required",
        "evidence",
        "status",
        "remarks"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(
                diagnosis,
                field,
                data[field]
            )

    db.session.commit()

    return jsonify({
        "message": "Diagnosis updated successfully",
        "diagnosis": {
            "id": diagnosis.id,
            "diagnosis_number": diagnosis.diagnosis_number,
            "status": diagnosis.status,
            "part_required": diagnosis.part_required
        }
    }), 200