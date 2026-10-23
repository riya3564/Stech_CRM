from sqlalchemy import MetaData, Table, select, func
from app import app
from extensions import db

with app.app_context():
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    checks = {
        "asc": ("asc_code", "DUMMY-"),
        "engineers": ("engineer_code", "DUMMY-"),
        "customers": ("customer_code", "DUMMY-"),
        "customer_products": ("customer_product_code", "DUMMY-"),
        "service_calls": ("call_id", "DUMMY-CALL-"),
    }

    for table_name, (column_name, prefix) in checks.items():
        table = metadata.tables.get(table_name)
        if table is None or column_name not in table.c:
            print(f"{table_name}: table/column missing")
            continue

        total = db.session.scalar(
            select(func.count()).select_from(table)
        )
        demo = db.session.scalar(
            select(func.count()).select_from(table).where(
                table.c[column_name].like(f"{prefix}%")
            )
        )
        print(f"{table_name}: total={total}, tagged_demo={demo}")

    print("\nLinked tables:")
    for name in [
        "asc_assignments", "appointments", "engineer_visits",
        "diagnoses", "repairs", "testings", "part_requirements",
        "customer_confirmations", "revisits"
    ]:
        table = metadata.tables.get(name)
        if table is not None:
            total = db.session.scalar(
                select(func.count()).select_from(table)
            )
            print(f"{name}: {total}")
