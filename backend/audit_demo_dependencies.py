import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "backend" / ".env")
load_dotenv(ROOT / ".env")

url = os.getenv("DATABASE_URL")
if not url:
    raise SystemExit("ERROR: DATABASE_URL not found in .env")

url = url.replace("postgresql+psycopg://", "postgresql://", 1)
engine = create_engine(url)
inspector = inspect(engine)
tables = inspector.get_table_names()

def q(name):
    return '"' + name.replace('"', '""') + '"'

with engine.connect() as conn:
    print("\n=== READ-ONLY DEMO DEPENDENCY AUDIT ===")
    print("Database connection: OK")
    tagged = {}

    for table in tables:
        columns = inspector.get_columns(table)
        pk_cols = inspector.get_pk_constraint(table).get("constrained_columns") or []
        if not pk_cols:
            continue

        text_cols = [
            c["name"] for c in columns
            if str(c["type"]).lower().startswith(
                ("varchar", "character varying", "text", "char")
            )
        ]
        if not text_cols:
            continue

        conditions = " OR ".join(
            f"CAST({q(c)} AS TEXT) LIKE 'DUMMY-%'" for c in text_cols
        )
        sql = text(
            f"SELECT {', '.join(q(c) for c in pk_cols)} "
            f"FROM {q(table)} WHERE {conditions}"
        )
        rows = conn.execute(sql).fetchall()
        if rows:
            tagged[table] = {
                "pk": pk_cols,
                "ids": [tuple(row) for row in rows],
            }
            print(f"TAGGED {table}: {len(rows)} row(s)")

    print("\n=== CHILD RECORDS LINKED TO TAGGED DEMO RECORDS ===")
    found = False

    for parent, info in tagged.items():
        if len(info["pk"]) != 1:
            print(f"REVIEW {parent}: composite primary key; not auto-counted")
            continue

        pk = info["pk"][0]
        ids = [r[0] for r in info["ids"]]

        for child in tables:
            for fk in inspector.get_foreign_keys(child):
                if fk.get("referred_table") != parent:
                    continue
                if fk.get("referred_columns") != [pk]:
                    continue

                child_col = fk["constrained_columns"][0]
                sql = text(
                    f"SELECT COUNT(*) FROM {q(child)} "
                    f"WHERE {q(child_col)} IN :ids"
                ).bindparams()
                # Use expanding bind parameter for the ID list.
                from sqlalchemy import bindparam
                sql = text(
                    f"SELECT COUNT(*) FROM {q(child)} "
                    f"WHERE {q(child_col)} IN :ids"
                ).bindparams(bindparam("ids", expanding=True))
                count = conn.execute(sql, {"ids": ids}).scalar_one()

                if count:
                    found = True
                    print(
                        f"{child}: {count} row(s) reference "
                        f"demo {parent} via {child_col}"
                    )

    if not found:
        print("No direct foreign-key dependencies found for tagged rows.")

    print("\nAudit complete. No records were inserted, updated, or deleted.")

engine.dispose()
