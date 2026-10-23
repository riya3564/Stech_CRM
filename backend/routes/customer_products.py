from datetime import date, datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from extensions import db
from models.customer import Customer
from models.customer_product import CustomerProduct
from models.customer_product_ownership_history import CustomerProductOwnershipHistory
from models.service_call import ServiceCall


customer_products_bp = Blueprint(
    "customer_products",
    __name__,
    url_prefix="/api/customer-products"
)


def generate_customer_product_code():
    last_product = db.session.scalar(
        select(CustomerProduct)
        .order_by(CustomerProduct.id.desc())
    )

    next_id = (last_product.id + 1) if last_product else 1
    return f"CPROD-{next_id:04d}"


def parse_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def get_warranty_status(customer_product):
    today = date.today()

    if not customer_product.warranty_start_date or not customer_product.warranty_end_date:
        return "NOT_CONFIGURED"

    if today < customer_product.warranty_start_date:
        return "NOT_STARTED"

    if customer_product.warranty_start_date <= today <= customer_product.warranty_end_date:
        return "IN_WARRANTY"

    return "EXPIRED"


def get_amc_status(customer_product):
    today = date.today()

    if not customer_product.amc_start_date or not customer_product.amc_end_date:
        return "NOT_CONFIGURED"

    if today < customer_product.amc_start_date:
        return "NOT_STARTED"

    if customer_product.amc_start_date <= today <= customer_product.amc_end_date:
        return "ACTIVE"

    return "EXPIRED"


@customer_products_bp.post("/")
def create_customer_product():
    data = request.get_json() or {}

    customer_id = data.get("customer_id")
    product_model_id = data.get("product_model_id")
    serial_number = (data.get("serial_number") or "").strip()

    if not customer_id:
        return jsonify({
            "message": "customer_id is required"
        }), 400

    if not product_model_id:
        return jsonify({
            "message": "product_model_id is required"
        }), 400

    if not serial_number:
        return jsonify({
            "message": "serial_number is required"
        }), 400

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({
            "message": "Customer not found"
        }), 404

    existing_serial = db.session.scalar(
        select(CustomerProduct).where(
            CustomerProduct.serial_number == serial_number
        )
    )

    if existing_serial:
        return jsonify({
            "message": "Serial number already exists",
            "customer_product_id": existing_serial.id,
            "customer_product_code": existing_serial.customer_product_code
        }), 409

    purchase_date = parse_date(data.get("purchase_date"))
    installation_date = parse_date(data.get("installation_date"))
    warranty_start_date = parse_date(data.get("warranty_start_date"))
    warranty_end_date = parse_date(data.get("warranty_end_date"))
    amc_start_date = parse_date(data.get("amc_start_date"))
    amc_end_date = parse_date(data.get("amc_end_date"))

    date_fields = {
        "purchase_date": purchase_date,
        "installation_date": installation_date,
        "warranty_start_date": warranty_start_date,
        "warranty_end_date": warranty_end_date,
        "amc_start_date": amc_start_date,
        "amc_end_date": amc_end_date
    }

    for field_name, parsed_value in date_fields.items():
        if data.get(field_name) and parsed_value is None:
            return jsonify({
                "message": f"Invalid date format for {field_name}. Use YYYY-MM-DD."
            }), 400

    if (
        warranty_start_date
        and warranty_end_date
        and warranty_end_date < warranty_start_date
    ):
        return jsonify({
            "message": "Warranty end date cannot be before warranty start date"
        }), 400

    if (
        amc_start_date
        and amc_end_date
        and amc_end_date < amc_start_date
    ):
        return jsonify({
            "message": "AMC end date cannot be before AMC start date"
        }), 400

    customer_product = CustomerProduct(
        customer_product_code=generate_customer_product_code(),
        customer_id=customer_id,
        product_model_id=product_model_id,
        serial_number=serial_number,
        purchase_date=purchase_date,
        installation_date=installation_date,
        warranty_start_date=warranty_start_date,
        warranty_end_date=warranty_end_date,
        amc_start_date=amc_start_date,
        amc_end_date=amc_end_date,
        status=data.get("status", "Active")
    )

    db.session.add(customer_product)
    db.session.flush()

    ownership_history = CustomerProductOwnershipHistory(
        customer_product_id=customer_product.id,
        customer_id=customer_id,
        valid_from=customer_product.created_at,
        valid_to=None,
        change_reason="Initial product ownership snapshot"
    )

    db.session.add(ownership_history)
    db.session.commit()

    return jsonify({
        "message": "Customer product created successfully",
        "customer_product": {
            "id": customer_product.id,
            "customer_product_code": customer_product.customer_product_code,
            "customer_id": customer_product.customer_id,
            "product_model_id": customer_product.product_model_id,
            "serial_number": customer_product.serial_number,
            "warranty_status": get_warranty_status(customer_product),
            "amc_status": get_amc_status(customer_product),
            "status": customer_product.status
        }
    }), 201


@customer_products_bp.get("/")
def list_customer_products():
    customer_products = db.session.scalars(
        select(CustomerProduct)
        .order_by(CustomerProduct.id.asc())
    ).all()

    result = []

    for customer_product in customer_products:
        result.append({
            "id": customer_product.id,
            "customer_product_code": customer_product.customer_product_code,
            "customer_id": customer_product.customer_id,
            "product_model_id": customer_product.product_model_id,
            "serial_number": customer_product.serial_number,
            "purchase_date": (
                customer_product.purchase_date.isoformat()
                if customer_product.purchase_date else None
            ),
            "installation_date": (
                customer_product.installation_date.isoformat()
                if customer_product.installation_date else None
            ),
            "warranty_start_date": (
                customer_product.warranty_start_date.isoformat()
                if customer_product.warranty_start_date else None
            ),
            "warranty_end_date": (
                customer_product.warranty_end_date.isoformat()
                if customer_product.warranty_end_date else None
            ),
            "amc_start_date": (
                customer_product.amc_start_date.isoformat()
                if customer_product.amc_start_date else None
            ),
            "amc_end_date": (
                customer_product.amc_end_date.isoformat()
                if customer_product.amc_end_date else None
            ),
            "warranty_status": get_warranty_status(customer_product),
            "amc_status": get_amc_status(customer_product),
            "status": customer_product.status
        })

    return jsonify(result), 200


@customer_products_bp.get("/<int:customer_product_id>")
def get_customer_product(customer_product_id):
    customer_product = db.session.get(
        CustomerProduct,
        customer_product_id
    )

    if not customer_product:
        return jsonify({
            "message": "Customer product not found"
        }), 404

    return jsonify({
        "id": customer_product.id,
        "customer_product_code": customer_product.customer_product_code,
        "customer_id": customer_product.customer_id,
        "product_model_id": customer_product.product_model_id,
        "serial_number": customer_product.serial_number,
        "purchase_date": (
            customer_product.purchase_date.isoformat()
            if customer_product.purchase_date else None
        ),
        "installation_date": (
            customer_product.installation_date.isoformat()
            if customer_product.installation_date else None
        ),
        "warranty_start_date": (
            customer_product.warranty_start_date.isoformat()
            if customer_product.warranty_start_date else None
        ),
        "warranty_end_date": (
            customer_product.warranty_end_date.isoformat()
            if customer_product.warranty_end_date else None
        ),
        "amc_start_date": (
            customer_product.amc_start_date.isoformat()
            if customer_product.amc_start_date else None
        ),
        "amc_end_date": (
            customer_product.amc_end_date.isoformat()
            if customer_product.amc_end_date else None
        ),
        "warranty_status": get_warranty_status(customer_product),
        "amc_status": get_amc_status(customer_product),
        "status": customer_product.status
    }), 200


@customer_products_bp.put("/<int:customer_product_id>")
def update_customer_product(customer_product_id):
    customer_product = db.session.get(
        CustomerProduct,
        customer_product_id
    )

    if not customer_product:
        return jsonify({
            "message": "Customer product not found"
        }), 404

    data = request.get_json() or {}

    if "customer_id" not in data:
        return jsonify({
            "message": "customer_id is required"
        }), 400

    new_customer_id = data.get("customer_id")

    new_customer = db.session.get(
        Customer,
        new_customer_id
    )

    if not new_customer:
        return jsonify({
            "message": "New customer not found"
        }), 404

    old_customer_id = customer_product.customer_id

    if old_customer_id == new_customer_id:
        return jsonify({
            "message": "Customer ownership unchanged",
            "ownership_changed": False,
            "customer_product_id": customer_product.id,
            "customer_id": customer_product.customer_id
        }), 200

    current_ownership = db.session.scalar(
        select(CustomerProductOwnershipHistory)
        .where(
            CustomerProductOwnershipHistory.customer_product_id
            == customer_product.id,
            CustomerProductOwnershipHistory.valid_to.is_(None)
        )
        .order_by(
            CustomerProductOwnershipHistory.valid_from.desc()
        )
    )

    now = datetime.now(timezone.utc)

    if current_ownership:
        current_ownership.valid_to = now
    else:
        old_ownership = CustomerProductOwnershipHistory(
            customer_product_id=customer_product.id,
            customer_id=old_customer_id,
            valid_from=customer_product.created_at,
            valid_to=now,
            change_reason="Initial ownership history backfill"
        )

        db.session.add(old_ownership)

    new_ownership = CustomerProductOwnershipHistory(
        customer_product_id=customer_product.id,
        customer_id=new_customer_id,
        valid_from=now,
        valid_to=None,
        change_reason=data.get(
            "change_reason",
            "Product ownership transferred"
        )
    )

    db.session.add(new_ownership)

    customer_product.customer_id = new_customer_id

    db.session.commit()

    return jsonify({
        "message": "Customer product ownership updated successfully",
        "ownership_changed": True,
        "customer_product_id": customer_product.id,
        "old_customer_id": old_customer_id,
        "new_customer_id": new_customer_id
    }), 200


@customer_products_bp.get("/<int:customer_product_id>/ownership-history")
def get_customer_product_ownership_history(customer_product_id):
    customer_product = db.session.get(
        CustomerProduct,
        customer_product_id
    )

    if not customer_product:
        return jsonify({
            "message": "Customer product not found"
        }), 404

    history = db.session.scalars(
        select(CustomerProductOwnershipHistory)
        .where(
            CustomerProductOwnershipHistory.customer_product_id
            == customer_product_id
        )
        .order_by(
            CustomerProductOwnershipHistory.valid_from.asc()
        )
    ).all()

    history_result = []

    for item in history:
        customer = db.session.get(
            Customer,
            item.customer_id
        )

        history_result.append({
            "id": item.id,
            "customer_product_id": item.customer_product_id,
            "customer_id": item.customer_id,
            "customer_name": customer.full_name if customer else None,
            "valid_from": (
                item.valid_from.isoformat()
                if item.valid_from else None
            ),
            "valid_to": (
                item.valid_to.isoformat()
                if item.valid_to else None
            ),
            "change_reason": item.change_reason,
            "created_at": (
                item.created_at.isoformat()
                if item.created_at else None
            )
        })

    current_customer = db.session.get(
        Customer,
        customer_product.customer_id
    )

    return jsonify({
        "customer_product_id": customer_product.id,
        "customer_product_code": customer_product.customer_product_code,
        "serial_number": customer_product.serial_number,
        "current_customer": {
            "customer_id": customer_product.customer_id,
            "customer_name": (
                current_customer.full_name
                if current_customer else None
            )
        },
        "history_count": len(history_result),
        "history": history_result
    }), 200


@customer_products_bp.get("/<int:customer_product_id>/history")
def get_customer_product_history(customer_product_id):
    customer_product = db.session.get(
        CustomerProduct,
        customer_product_id
    )

    if not customer_product:
        return jsonify({
            "message": "Customer product not found"
        }), 404

    service_calls = db.session.scalars(
        select(ServiceCall)
        .where(
            ServiceCall.customer_product_id == customer_product_id
        )
        .order_by(ServiceCall.id.asc())
    ).all()

    history = []

    for call in service_calls:
        history.append({
            "service_call_id": call.id,
            "call_code": call.call_code,
            "customer_id": call.customer_id,
            "complaint": call.complaint,
            "serviceability_status": call.serviceability_status,
            "duplicate_status": call.duplicate_status,
            "status": call.status,
            "created_at": (
                call.created_at.isoformat()
                if call.created_at else None
            )
        })

    return jsonify({
        "customer_product_id": customer_product.id,
        "customer_product_code": customer_product.customer_product_code,
        "serial_number": customer_product.serial_number,
        "history_count": len(history),
        "history": history
    }), 200