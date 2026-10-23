from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.customer import Customer
from models.customer_address_history import CustomerAddressHistory


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers"
)


@customers_bp.get("")
@jwt_required()
def get_customers():
    customers = db.session.scalars(
        db.select(Customer).order_by(Customer.id.desc())
    ).all()

    return jsonify([
        {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "mobile": customer.mobile,
            "email": customer.email,
            "customer_type": customer.customer_type,
            "address_line": customer.address_line,
            "city": customer.city,
            "state": customer.state,
            "pin_code": customer.pin_code,
            "status": customer.status,
            "created_at": customer.created_at.isoformat(),
        }
        for customer in customers
    ]), 200


@customers_bp.post("")
@jwt_required()
def create_customer():
    data = request.get_json() or {}

    required_fields = [
        "customer_code",
        "full_name",
        "mobile"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "message": f"{field} is required."
            }), 400

    existing_customer = db.session.scalar(
        db.select(Customer).where(
            Customer.customer_code == data["customer_code"]
        )
    )

    if existing_customer:
        return jsonify({
            "message": "Customer code already exists."
        }), 409

    customer = Customer(
        customer_code=data["customer_code"].strip(),
        full_name=data["full_name"].strip(),
        mobile=data["mobile"].strip(),
        email=data.get("email"),
        customer_type=data.get("customer_type", "Individual"),
        address_line=data.get("address_line"),
        city=data.get("city"),
        state=data.get("state"),
        pin_code=data.get("pin_code"),
        status=data.get("status", "Active"),
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify({
        "message": "Customer created successfully.",
        "customer": {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "mobile": customer.mobile,
            "email": customer.email,
            "customer_type": customer.customer_type,
            "address_line": customer.address_line,
            "city": customer.city,
            "state": customer.state,
            "pin_code": customer.pin_code,
            "status": customer.status,
        }
    }), 201


@customers_bp.put("/<int:customer_id>")
@jwt_required()
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({
            "message": "Customer not found."
        }), 404

    data = request.get_json() or {}

    address_fields = [
        "address_line",
        "city",
        "state",
        "pin_code"
    ]

    address_changed = any(
        field in data and data.get(field) != getattr(customer, field)
        for field in address_fields
    )

    now = datetime.now(timezone.utc)

    if address_changed:
        current_history = db.session.scalar(
            db.select(CustomerAddressHistory)
            .where(
                CustomerAddressHistory.customer_id == customer.id,
                CustomerAddressHistory.valid_to.is_(None)
            )
            .order_by(
                CustomerAddressHistory.valid_from.desc()
            )
        )

        if current_history:
            current_history.valid_to = now
        else:
            old_address_history = CustomerAddressHistory(
                customer_id=customer.id,
                address_line=customer.address_line,
                city=customer.city,
                state=customer.state,
                pin_code=customer.pin_code,
                valid_from=customer.created_at,
                valid_to=now,
                change_reason="Previous address before update"
            )

            db.session.add(old_address_history)

        new_address_history = CustomerAddressHistory(
            customer_id=customer.id,
            address_line=data.get(
                "address_line",
                customer.address_line
            ),
            city=data.get(
                "city",
                customer.city
            ),
            state=data.get(
                "state",
                customer.state
            ),
            pin_code=data.get(
                "pin_code",
                customer.pin_code
            ),
            valid_from=now,
            valid_to=None,
            change_reason=data.get(
                "address_change_reason",
                "Customer address updated"
            )
        )

        db.session.add(new_address_history)

    if "full_name" in data:
        customer.full_name = data["full_name"].strip()

    if "mobile" in data:
        customer.mobile = data["mobile"].strip()

    if "email" in data:
        customer.email = data.get("email")

    if "customer_type" in data:
        customer.customer_type = data.get("customer_type")

    if "address_line" in data:
        customer.address_line = data.get("address_line")

    if "city" in data:
        customer.city = data.get("city")

    if "state" in data:
        customer.state = data.get("state")

    if "pin_code" in data:
        customer.pin_code = data.get("pin_code")

    if "status" in data:
        customer.status = data.get("status")

    db.session.commit()

    return jsonify({
        "message": "Customer updated successfully.",
        "address_changed": address_changed,
        "customer": {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "mobile": customer.mobile,
            "email": customer.email,
            "customer_type": customer.customer_type,
            "address_line": customer.address_line,
            "city": customer.city,
            "state": customer.state,
            "pin_code": customer.pin_code,
            "status": customer.status,
            "updated_at": customer.updated_at.isoformat(),
        }
    }), 200


@customers_bp.get("/<int:customer_id>/address-history")
@jwt_required()
def get_customer_address_history(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({
            "message": "Customer not found."
        }), 404

    history = db.session.scalars(
        db.select(CustomerAddressHistory)
        .where(
            CustomerAddressHistory.customer_id == customer_id
        )
        .order_by(
            CustomerAddressHistory.valid_from.desc()
        )
    ).all()

    return jsonify({
        "customer": {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "current_address": {
                "address_line": customer.address_line,
                "city": customer.city,
                "state": customer.state,
                "pin_code": customer.pin_code,
            }
        },
        "history_count": len(history),
        "history": [
            {
                "id": item.id,
                "address_line": item.address_line,
                "city": item.city,
                "state": item.state,
                "pin_code": item.pin_code,
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
                ),
            }
            for item in history
        ]
    }), 200