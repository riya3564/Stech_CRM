from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.brand import Brand
from utils.rbac import role_required


brands_bp = Blueprint(
    "brands",
    __name__,
    url_prefix="/api/brands"
)


def brand_to_dict(brand):
    return {
        "id": brand.id,
        "brand_code": brand.brand_code,
        "brand_name": brand.brand_name,
        "description": brand.description,
        "status": brand.status,
        "created_at": brand.created_at.isoformat(),
        "updated_at": brand.updated_at.isoformat(),
    }


# =========================================================
# GET ALL BRANDS
# Any authenticated user can view brands
# =========================================================
@brands_bp.get("")
@jwt_required()
def get_brands():

    brands = db.session.scalars(
        db.select(Brand)
        .order_by(Brand.brand_name.asc())
    ).all()

    return jsonify([
        brand_to_dict(brand)
        for brand in brands
    ]), 200


# =========================================================
# CREATE BRAND
# Only Super Admin can create a brand
# =========================================================
@brands_bp.post("")
@role_required("Super Admin")
def create_brand():

    data = request.get_json() or {}

    brand_code = data.get("brand_code", "").strip()
    brand_name = data.get("brand_name", "").strip()

    if not brand_code:
        return jsonify({
            "message": "brand_code is required."
        }), 400

    if not brand_name:
        return jsonify({
            "message": "brand_name is required."
        }), 400

    existing_code = db.session.scalar(
        db.select(Brand).where(
            Brand.brand_code == brand_code
        )
    )

    if existing_code:
        return jsonify({
            "message": "Brand code already exists."
        }), 409

    existing_name = db.session.scalar(
        db.select(Brand).where(
            Brand.brand_name == brand_name
        )
    )

    if existing_name:
        return jsonify({
            "message": "Brand name already exists."
        }), 409

    brand = Brand(
        brand_code=brand_code,
        brand_name=brand_name,
        description=data.get("description"),
        status=data.get("status", "Active"),
    )

    db.session.add(brand)
    db.session.commit()

    return jsonify({
        "message": "Brand created successfully.",
        "brand": brand_to_dict(brand)
    }), 201