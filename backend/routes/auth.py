from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required."
        }), 400

    user = db.session.scalar(
        db.select(User).where(User.email == email)
    )

    if not user or not user.check_password(password):
        return jsonify({
            "message": "Invalid email or password."
        }), 401

    if not user.is_active:
        return jsonify({
            "message": "User account is inactive."
        }), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role.name
        }
    )

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "role": user.role.name
        }
    }), 200
