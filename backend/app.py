from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from extensions import db, jwt

from routes.auth import auth_bp
from routes.customers import customers_bp
from routes.customer_products import customer_products_bp
from routes.call_types import call_types_bp
from routes.brands import brands_bp
from routes.product_categories import product_categories_bp
from routes.product_types import product_types_bp
from routes.product_models import product_models_bp
from routes.symptom_codes import symptom_codes_bp
from routes.fault_codes import fault_codes_bp
from routes.diagnosis_codes import diagnosis_codes_bp
from routes.repair_codes import repair_codes_bp
from routes.parts import parts_bp
from routes.part_compatibility import part_compatibility_bp
from routes.service_calls import service_calls_bp
from routes.serviceability import serviceability_bp
from routes.asc import asc_bp
from routes.asc_assignments import asc_assignments_bp
from routes.engineers import engineers_bp
from routes.appointments import appointments_bp
from routes.engineer_visits import engineer_visits_bp
from routes.diagnoses import diagnoses_bp
from routes.repairs import repairs_bp
from routes.part_requirements import part_requirements_bp
from routes.inventory import inventory_bp
from routes.testing import testing_bp
from routes.customer_confirmations import customer_confirmations_bp
from routes.revisits import revisits_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    db.init_app(app)
    jwt.init_app(app)

    # Flask-Migrate
    Migrate(app, db)

    # API Routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(customer_products_bp)
    app.register_blueprint(call_types_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(product_categories_bp)
    app.register_blueprint(product_types_bp)
    app.register_blueprint(product_models_bp)
    app.register_blueprint(symptom_codes_bp)
    app.register_blueprint(fault_codes_bp)
    app.register_blueprint(diagnosis_codes_bp)
    app.register_blueprint(repair_codes_bp)
    app.register_blueprint(parts_bp)
    app.register_blueprint(part_compatibility_bp)
    app.register_blueprint(service_calls_bp)
    app.register_blueprint(serviceability_bp)
    app.register_blueprint(asc_bp)
    app.register_blueprint(asc_assignments_bp)
    app.register_blueprint(engineers_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(engineer_visits_bp)
    app.register_blueprint(diagnoses_bp)
    app.register_blueprint(repairs_bp)
    app.register_blueprint(part_requirements_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(testing_bp)
    app.register_blueprint(customer_confirmations_bp)
    app.register_blueprint(revisits_bp)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "STech ServiceCRM",
            "description": "Enterprise Service Operations"
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )