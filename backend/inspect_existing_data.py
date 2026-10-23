from sqlalchemy import inspect, text
from app import app
from extensions import db

with app.app_context():
    inspector = inspect(db.engine)

    print("\n===== CUSTOMER TABLE COLUMNS =====")
    customer_cols = [
        c["name"] for c in inspector.get_columns("customers")
    ]
    print(", ".join(customer_cols))

    print("\n===== SAMPLE CUSTOMER RECORDS =====")
    with db.engine.connect() as conn:
        if "id" in customer_cols:
            cols = ["id"]
            for candidate in ("name", "full_name", "customer_name",
                              "mobile", "phone", "email", "city"):
                if candidate in customer_cols:
                    cols.append(candidate)
            query_cols = ", ".join(f'"{c}"' for c in cols)
            rows = conn.execute(text(
                f'SELECT {query_cols} FROM customers ORDER BY id LIMIT 10'
            )).mappings()
            for row in rows:
                item = dict(row)
                for key in ("mobile", "phone"):
                    if item.get(key):
                        value = str(item[key])
                        item[key] = "*" * max(0, len(value)-4) + value[-4:]
                print(item)

    print("\n===== SERVICE CALL STATUS COUNTS =====")
    call_cols = [c["name"] for c in inspector.get_columns("service_calls")]
    print("Columns:", ", ".join(call_cols))
    with db.engine.connect() as conn:
        for candidate in ("status", "call_status"):
            if candidate in call_cols:
                rows = conn.execute(text(
                    f'SELECT "{candidate}", COUNT(*) FROM service_calls '
                    f'GROUP BY "{candidate}" ORDER BY COUNT(*) DESC'
                ))
                for row in rows:
                    print(row)
                break
