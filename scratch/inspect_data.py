import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("db/nifty100.db")
conn = sqlite3.connect(db_path)

print("--- SQLITE TABLES ---")
tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for t in tables:
    df = pd.read_sql_query(f"SELECT * FROM {t} LIMIT 2", conn)
    cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"\nTable '{t}' ({cnt} rows):")
    print(df.columns.tolist())

print("\n--- SUPPORTING DATASETS ---")
sup_dir = Path("supporting_datasets")
for f in sup_dir.glob("*.xlsx"):
    try:
        df = pd.read_excel(f)
        print(f"\nFile '{f.name}' ({len(df)} rows):")
        print(df.columns.tolist())
        print(df.head(2))
    except Exception as e:
        print(f"Error reading {f}: {e}")

conn.close()
