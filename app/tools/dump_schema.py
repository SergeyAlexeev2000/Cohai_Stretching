import sqlite3
from pathlib import Path

DB_PATH = "cohai_stretching.db"
OUT_PATH = Path("docs/schema_2025-11-24.sql")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

schema = "\n".join(row[0] for row in cursor.execute("SELECT sql FROM sqlite_master WHERE sql NOT NULL;"))

OUT_PATH.write_text(schema, encoding="utf-8")

print(f"Schema exported to {OUT_PATH}")
