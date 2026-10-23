from app import app
from extensions import db
from models.user import Role, User

with app.app_context():
    db.create_all()

    admin_role = db.session.scalar(
        db.select(Role).where(Role.name == "Super Admin")
    )

    if not admin_role:
        admin_role = Role(
            name="Super Admin",
            description="Full system administration access"
        )
        db.session.add(admin_role)
        db.session.flush()

    admin = db.session.scalar(
        db.select(User).where(
            User.email == "admin@servicecrm.local"
        )
    )

    if not admin:
        admin = User(
            full_name="System Administrator",
            email="admin@servicecrm.local",
            role_id=admin_role.id
        )
        admin.set_password("Admin@12345")
        db.session.add(admin)

    db.session.commit()

    print("Database tables created successfully.")
    print("Admin user ready.")