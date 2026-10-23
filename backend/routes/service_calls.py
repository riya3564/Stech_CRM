from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import select, and_

from extensions import db

from models.service_call import ServiceCall
from models.asc import ASC
from models.asc_assignment import ASCAssignment
from models.customer_product import CustomerProduct
from models.serviceability import Serviceability
from models.product_model import ProductModel
from models.call_type import CallType


service_calls_bp = Blueprint(
    "service_calls",
    __name__,
    url_prefix="/api/service-calls"
)


# =========================================================
# STATE AND DISTRICT CODES
# =========================================================

STATE_CODES = {
    "andhra pradesh": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CG",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OD",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN",
    "telangana": "TS",
    "tripura": "TR",
    "uttar pradesh": "UP",
    "uttarakhand": "UK",
    "west bengal": "WB",
    "delhi": "DL",
    "chandigarh": "CH",
    "puducherry": "PY",
    "jammu and kashmir": "JK",
    "ladakh": "LA",
}

DISTRICT_CODES = {
    ("uttarakhand", "almora"): "01",
    ("uttarakhand", "bageshwar"): "02",
    ("uttarakhand", "chamoli"): "03",
    ("uttarakhand", "nainital"): "04",
    ("uttarakhand", "champawat"): "05",
    ("uttarakhand", "udham singh nagar"): "06",
    ("uttarakhand", "dehradun"): "07",
    ("uttarakhand", "haridwar"): "08",
    ("uttarakhand", "tehri garhwal"): "09",
    ("uttarakhand", "uttarkashi"): "10",
    ("uttarakhand", "pithoragarh"): "11",
    ("uttarakhand", "pauri garhwal"): "12",
    ("uttarakhand", "rudraprayag"): "13",
    ("uttar pradesh", "agra"): "09",
    ("uttar pradesh", "aligarh"): "11",
    ("uttar pradesh", "prayagraj"): "44",
    ("uttar pradesh", "bareilly"): "25",
    ("uttar pradesh", "budaun"): "24",
    ("uttar pradesh", "bulandshahr"): "13",
    ("uttar pradesh", "ghaziabad"): "14",
    ("uttar pradesh", "gautam buddha nagar"): "16",
    ("uttar pradesh", "noida"): "16",
    ("uttar pradesh", "greater noida"): "16",
    ("uttar pradesh", "gorakhpur"): "53",
    ("uttar pradesh", "lucknow"): "32",
    ("uttar pradesh", "meerut"): "15",
    ("uttar pradesh", "moradabad"): "21",
    ("uttar pradesh", "varanasi"): "65",
    ("delhi", "central delhi"): "01",
    ("delhi", "east delhi"): "02",
    ("delhi", "new delhi"): "03",
    ("delhi", "north delhi"): "04",
    ("delhi", "north east delhi"): "05",
    ("delhi", "north west delhi"): "06",
    ("delhi", "south delhi"): "07",
    ("delhi", "south east delhi"): "08",
    ("delhi", "south west delhi"): "09",
    ("delhi", "west delhi"): "10",
    ("haryana", "gurugram"): "01",
    ("haryana", "gurgaon"): "01",
    ("haryana", "faridabad"): "02",
    ("haryana", "panipat"): "06",
    ("haryana", "ambala"): "01",
}


# =========================================================
# GENERAL HELPERS
# =========================================================

def normalize_text(value):
    return str(value).strip().lower() if value is not None else ""


def get_state_code(state):
    value = normalize_text(state)
    return STATE_CODES.get(value, value[:2].upper())


def get_district_code(state, district):
    return DISTRICT_CODES.get(
        (normalize_text(state), normalize_text(district)),
        "00"
    )


def get_call_type_code(call_type):
    if not call_type:
        return "R"

    code = normalize_text(
        getattr(call_type, "call_type_code", "")
    )
    name = normalize_text(
        getattr(call_type, "call_type_name", "")
    )
    value = code or name

    if "install" in value:
        return "I"
    if "breakdown" in value:
        return "B"

    return "R"


def get_brand_code(product_model):
    brand = (
        getattr(product_model, "brand", None)
        if product_model else None
    )

    if not brand:
        return "BRD"

    code = getattr(brand, "brand_code", None)
    name = getattr(brand, "brand_name", None)

    return str(
        code or (name[:3] if name else "BRD")
    ).upper()


def get_product_type_code(product_model):
    product_type = (
        getattr(product_model, "product_type", None)
        if product_model else None
    )

    if not product_type:
        return "PRD"

    code = getattr(product_type, "product_type_code", None)
    name = getattr(product_type, "product_type_name", None)

    return str(
        code or (name[:3] if name else "PRD")
    ).upper()


def generate_call_id():
    last_call = db.session.scalar(
        select(ServiceCall).order_by(ServiceCall.id.desc())
    )

    next_number = 1

    if last_call and last_call.call_id:
        try:
            next_number = int(
                last_call.call_id.split("-")[-1]
            ) + 1
        except (ValueError, AttributeError):
            next_number = last_call.id + 1

    return f"CALL-{next_number:04d}"


def generate_complaint_id(
    state,
    district,
    product_model,
    call_type,
    service_call_id
):
    date_code = datetime.now(timezone.utc).strftime("%Y%m%d")

    return (
        f"{get_state_code(state)}"
        f"{get_district_code(state, district)}"
        f"-{get_brand_code(product_model)}"
        f"-{get_product_type_code(product_model)}"
        f"-{date_code}"
        f"-{service_call_id:06d}"
        f"-{get_call_type_code(call_type)}"
    )


def iso(value):
    return value.isoformat() if value else None


# =========================================================
# SERVICE CALL SERIALIZER
# =========================================================

def serialize_service_call(service_call):
    customer = getattr(service_call, "customer", None)
    customer_product = getattr(
        service_call, "customer_product", None
    )
    product = getattr(service_call, "product_model", None)
    call_type = getattr(service_call, "call_type", None)
    symptom = getattr(service_call, "symptom", None)

    brand = getattr(product, "brand", None) if product else None
    product_type = (
        getattr(product, "product_type", None)
        if product else None
    )

    customer_name = (
        getattr(customer, "full_name", None)
        if customer else None
    )
    customer_mobile = (
        getattr(customer, "mobile", None)
        if customer else None
    )
    customer_code = (
        getattr(customer, "customer_code", None)
        if customer else None
    )

    model_name = (
        getattr(product, "model_name", None)
        if product else None
    )
    model_number = (
        getattr(product, "model_number", None)
        if product else None
    )

    return {
        "id": service_call.id,
        "call_id": service_call.call_id,
        "complaint_id": service_call.complaint_id,

        "customer_id": service_call.customer_id,
        "customer_name": customer_name,
        "customer_full_name": customer_name,
        "customer_phone": customer_mobile,
        "customer_mobile": customer_mobile,
        "mobile": customer_mobile,
        "customer_number": customer_code,
        "customer_code": customer_code,
        "customer_email": (
            getattr(customer, "email", None)
            if customer else None
        ),

        "customer_product_id": service_call.customer_product_id,
        "product_model_id": service_call.product_model_id,
        "product_name": model_name or model_number,
        "product_model_name": model_name or model_number,
        "model_name": model_name,
        "model_number": model_number,
        "brand_name": (
            getattr(brand, "brand_name", None)
            if brand else None
        ),
        "product_type_name": (
            getattr(product_type, "product_type_name", None)
            if product_type else None
        ),

        "call_type_id": service_call.call_type_id,
        "call_type_name": (
            getattr(call_type, "call_type_name", None)
            if call_type else None
        ),
        "call_type_code": (
            getattr(call_type, "call_type_code", None)
            if call_type else None
        ),

        "symptom_id": service_call.symptom_id,
        "symptom_name": (
            getattr(symptom, "symptom_name", None)
            if symptom else None
        ),
        "symptom_code": (
            getattr(symptom, "symptom_code", None)
            if symptom else None
        ),

        "serial_number": (
            service_call.serial_number
            or (
                getattr(customer_product, "serial_number", None)
                if customer_product else None
            )
        ),

        "complaint_description": service_call.complaint_description,
        "service_address": service_call.service_address,
        "city": service_call.city,
        "state": service_call.state,
        "pin_code": service_call.pin_code,
        "priority": service_call.priority,
        "status": service_call.status,
        "bucket": (
            "Open"
            if service_call.status == "Open"
            else service_call.status
        ),
        "serviceability_status": service_call.serviceability_status,
        "duplicate_check_status": service_call.duplicate_check_status,
        "registered_at": iso(service_call.registered_at),
        "sla_start_at": iso(service_call.sla_start_at),
        "sla_due_at": iso(service_call.sla_due_at),
    }


def get_current_asc(service_call_id):
    assignment = db.session.scalar(
        select(ASCAssignment)
        .where(
            ASCAssignment.service_call_id == service_call_id
        )
        .order_by(ASCAssignment.id.desc())
    )

    if not assignment:
        return None

    return db.session.get(ASC, assignment.asc_id)


# =========================================================
# CREATE SERVICE CALL
# =========================================================

@service_calls_bp.post("")
def create_service_call():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "customer_id",
        "product_model_id",
        "call_type_id",
        "symptom_id",
        "complaint_description",
        "state",
        "district",
    ]

    missing_fields = [
        field for field in required_fields
        if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "message": "Required fields are missing",
            "missing_fields": missing_fields,
        }), 400

    product_model = db.session.get(
        ProductModel, data["product_model_id"]
    )

    if not product_model:
        return jsonify({
            "message": "Product model not found"
        }), 404

    call_type = db.session.get(
        CallType, data["call_type_id"]
    )

    if not call_type:
        return jsonify({
            "message": "Call type not found"
        }), 404

    customer_product = None

    if data.get("customer_product_id") is not None:
        customer_product = db.session.get(
            CustomerProduct,
            data["customer_product_id"]
        )

        if not customer_product:
            return jsonify({
                "message": "Customer product not found"
            }), 404

        if customer_product.customer_id != data["customer_id"]:
            return jsonify({
                "message": (
                    "Customer product does not belong "
                    "to this customer"
                )
            }), 400

        if (
            customer_product.product_model_id
            != data["product_model_id"]
        ):
            return jsonify({
                "message": (
                    "Customer product does not match "
                    "selected product model"
                )
            }), 400

        if (
            data.get("serial_number")
            and data["serial_number"]
            != customer_product.serial_number
        ):
            return jsonify({
                "message": (
                    "Serial number does not belong "
                    "to selected customer product"
                ),
                "expected_serial_number": (
                    customer_product.serial_number
                ),
                "provided_serial_number": data["serial_number"],
            }), 400

    duplicate_conditions = [
        ServiceCall.customer_id == data["customer_id"],
        ServiceCall.product_model_id == data["product_model_id"],
        ServiceCall.status.in_([
            "Open",
            "Registered",
            "Validated",
            "Assigned",
            "Appointment Scheduled",
            "In Progress",
            "Repair In Progress",
            "Part Required",
            "Part Pending",
            "Revisit",
        ]),
    ]

    if data.get("serial_number"):
        duplicate_conditions.append(
            ServiceCall.serial_number == data["serial_number"]
        )

    existing_open_call = db.session.scalar(
        select(ServiceCall).where(
            and_(*duplicate_conditions)
        )
    )

    if existing_open_call:
        return jsonify({
            "message": (
                "An open complaint already exists "
                "for this customer/product"
            ),
            "duplicate_check_status": "Duplicate",
            "existing_call_id": existing_open_call.call_id,
            "existing_complaint_id": (
                existing_open_call.complaint_id
            ),
        }), 409

    pin_code = (data.get("pin_code") or "").strip()
    serviceability_status = "NOT_CONFIGURED"

    if pin_code:
        record = db.session.scalar(
            select(Serviceability).where(
                Serviceability.pin_code == pin_code,
                Serviceability.status == "Active",
            )
        )

        if record:
            serviceability_status = (
                "Serviceable"
                if record.serviceable
                else "Non-Serviceable"
            )

    registered_at = datetime.now(timezone.utc)

    service_call = ServiceCall(
        call_id=generate_call_id(),
        complaint_id=None,
        customer_product_id=data.get("customer_product_id"),
        customer_id=data["customer_id"],
        product_model_id=data["product_model_id"],
        call_type_id=data["call_type_id"],
        symptom_id=data["symptom_id"],
        serial_number=data.get("serial_number"),
        complaint_description=data["complaint_description"],
        service_address=data.get("service_address"),
        city=data.get("city"),
        state=data.get("state"),
        pin_code=pin_code or None,
        priority=data.get("priority", "Normal"),
        status="Open",
        serviceability_status=serviceability_status,
        duplicate_check_status="Clear",
        registered_at=registered_at,
        sla_start_at=registered_at,
        sla_due_at=registered_at + timedelta(hours=48),
    )

    db.session.add(service_call)
    db.session.flush()

    assigned_asc = None

    if pin_code:
        assigned_asc = db.session.scalar(
            select(ASC)
            .where(
                ASC.pin_code == pin_code,
                ASC.status == "Active"
            )
            .order_by(ASC.id.asc())
        )

        if assigned_asc:
            db.session.add(ASCAssignment(
                service_call_id=service_call.id,
                asc_id=assigned_asc.id,
                assignment_status="Assigned",
                assigned_at=datetime.now(timezone.utc),
                remarks=(
                    "Automatically assigned based on "
                    "customer PIN code"
                ),
            ))

            service_call.status = "Assigned"

    service_call.complaint_id = generate_complaint_id(
        data["state"],
        data["district"],
        product_model,
        call_type,
        service_call.id,
    )

    db.session.commit()

    result = serialize_service_call(service_call)

    result.update({
        "state_code": get_state_code(data["state"]),
        "district": data["district"],
        "district_code": get_district_code(
            data["state"], data["district"]
        ),
        "brand_code": get_brand_code(product_model),
        "product_type_code": get_product_type_code(product_model),
        "asc_id": assigned_asc.id if assigned_asc else None,
        "asc_code": assigned_asc.asc_code if assigned_asc else None,
        "asc_name": assigned_asc.asc_name if assigned_asc else None,
        "engineer_id": getattr(
            service_call, "engineer_id", None
        ),
    })

    return jsonify({
        "message": "Service complaint registered successfully",
        "service_call": result,
    }), 201


# =========================================================
# GET ALL SERVICE CALLS
# =========================================================

@service_calls_bp.get("")
def get_service_calls():
    service_calls = db.session.scalars(
        select(ServiceCall).order_by(ServiceCall.id.desc())
    ).all()

    return jsonify([
        serialize_service_call(item)
        for item in service_calls
    ])


# =========================================================
# OPEN BUCKET
# =========================================================

@service_calls_bp.get("/open")
def get_open_service_calls():
    service_calls = db.session.scalars(
        select(ServiceCall)
        .where(ServiceCall.status == "Open")
        .order_by(ServiceCall.id.desc())
    ).all()

    results = []

    for item in service_calls:
        result = serialize_service_call(item)
        result["bucket"] = "Open"
        results.append(result)

    return jsonify(results)


# =========================================================
# GET SINGLE SERVICE CALL
# =========================================================

@service_calls_bp.get("/<int:service_call_id>")
def get_service_call(service_call_id):
    service_call = db.session.get(
        ServiceCall, service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service complaint not found"
        }), 404

    result = serialize_service_call(service_call)
    assigned_asc = get_current_asc(service_call.id)

    result.update({
        "asc_id": assigned_asc.id if assigned_asc else None,
        "asc_code": (
            assigned_asc.asc_code if assigned_asc else None
        ),
        "asc_name": (
            assigned_asc.asc_name if assigned_asc else None
        ),
        "engineer_id": getattr(
            service_call, "engineer_id", None
        ),
    })

    return jsonify(result)


# =========================================================
# SERVICE CALL STATUS TRANSITION
# FIX: SUPPORT POST, PATCH AND PUT
# =========================================================

@service_calls_bp.route(
    "/<int:service_call_id>/status",
    methods=["POST", "PATCH", "PUT"]
)
def update_service_call_status(service_call_id):
    service_call = db.session.get(
        ServiceCall, service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service complaint not found"
        }), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if not isinstance(new_status, str) or not new_status.strip():
        return jsonify({
            "message": "status is required"
        }), 400

    new_status = new_status.strip()

    allowed_statuses = [
        "Open",
        "Registered",
        "Validated",
        "Assigned",
        "Appointment Scheduled",
        "In Progress",
        "Part Required",
        "Part Pending",
        "Repair In Progress",
        "Repair Completed",
        "Testing",
        "Customer Confirmation",
        "Revisit",
        "Closed",
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "message": "Invalid service call status",
            "allowed_statuses": allowed_statuses,
        }), 400

    current_status = service_call.status

    if current_status == "Closed":
        return jsonify({
            "message": (
                "Closed service complaint cannot be "
                "moved to another status"
            ),
            "status": current_status,
        }), 409

    if current_status == new_status:
        return jsonify({
            "message": (
                f"Service complaint is already in status "
                f"'{new_status}'"
            ),
            "status": current_status,
        }), 409

    if (
        new_status == "Repair In Progress"
        and current_status not in [
            "Part Required",
            "Part Pending",
            "In Progress",
            "Repair Completed",
        ]
    ):
        return jsonify({
            "message": (
                "Service call cannot move to Repair In Progress "
                "from current status"
            ),
            "current_status": current_status,
        }), 409

    if (
        new_status == "Testing"
        and current_status != "Repair Completed"
    ):
        return jsonify({
            "message": (
                "Testing can start only after Repair Completed"
            ),
            "current_status": current_status,
        }), 409

    if (
        new_status == "Customer Confirmation"
        and current_status != "Testing"
    ):
        return jsonify({
            "message": (
                "Customer Confirmation can start only after Testing"
            ),
            "current_status": current_status,
        }), 409

    if (
        new_status == "Closed"
        and current_status != "Customer Confirmation"
    ):
        return jsonify({
            "message": (
                "Service complaint can be Closed only after "
                "Customer Confirmation"
            ),
            "current_status": current_status,
        }), 409

    try:
        service_call.status = new_status
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": "Failed to update service call status"
        }), 500

    return jsonify({
        "message": "Service call status updated successfully",
        "service_call": {
            "id": service_call.id,
            "call_id": service_call.call_id,
            "complaint_id": service_call.complaint_id,
            "previous_status": current_status,
            "status": service_call.status,
            "bucket": (
                "Open"
                if service_call.status == "Open"
                else service_call.status
            ),
        },
    }), 200


# =========================================================
# SERVICE CALL CLOSURE
# =========================================================

@service_calls_bp.post("/<int:service_call_id>/close")
def close_service_call(service_call_id):
    service_call = db.session.get(
        ServiceCall, service_call_id
    )

    if not service_call:
        return jsonify({
            "message": "Service complaint not found"
        }), 404

    if service_call.status == "Closed":
        return jsonify({
            "message": "Service complaint is already closed"
        }), 409

    if service_call.status != "Customer Confirmation":
        return jsonify({
            "message": (
                "Service complaint cannot be closed before "
                "Customer Confirmation"
            ),
            "current_status": service_call.status,
        }), 409

    service_call.status = "Closed"
    db.session.commit()

    return jsonify({
        "message": "Service complaint closed successfully",
        "service_call": {
            "id": service_call.id,
            "call_id": service_call.call_id,
            "complaint_id": service_call.complaint_id,
            "status": service_call.status,
            "bucket": service_call.status,
        },
    }), 200