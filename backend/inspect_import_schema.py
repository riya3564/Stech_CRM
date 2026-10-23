
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

# Read DATABASE_URL from the backend .env file
env_path = Path(__file__).resolve().parent / ".env"

if not env_path.exists():
    raise FileNotFoundError(f".env file not found: {env_path}")

env_values = {}
for line in env_path.read_text(encoding="utf-8-sig").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    env_values[key.strip()] = value.strip().strip('"').strip("'")

database_url = env_values.get("DATABASE_URL") or os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL was not found in backend/.env")

engine = create_engine(database_url, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        inspector = inspect(connection)
        tables = inspector.get_table_names()

        print("\nDatabase connection successful.")
        print(f"Tables found: {len(tables)}")

        for table in sorted(tables):
            columns = [
                column["name"]
                for column in inspector.get_columns(table)
            ]
            print(f"\n{table}")
            print("  Columns: " + ", ".join(columns))

finally:
    engine.dispose()
