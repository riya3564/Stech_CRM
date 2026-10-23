from sqlalchemy import inspect, text
from app import app
from extensions import db

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print("\n===== CONNECTED DATABASE =====")
    with db.engine.connect() as conn:
        print(conn.execute(text(
            "SELECT current_database(), current_user"
        )).one())

    print("\n===== TABLES AND RECORD COUNTS =====")
    with db.engine.connect() as conn:
        for table in sorted(tables):
            try:
                count = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{table}"')
                ).scalar_one()
                print(f"{table}: {count} records")
            except Exception as e:
                print(f"{table}: count failed ({type(e).__name__})")
