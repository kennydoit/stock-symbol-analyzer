import sqlite3
import yaml
from pathlib import Path
import os

# Load config.yaml to get db_path
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Resolve db_path from config, handling $project_root
raw_db_path = config.get("stock_db_path", "stock_database.db")
project_root = Path(__file__).resolve().parent.parent.parent
print(f"Project root directory: {project_root}")
if raw_db_path.startswith("$project_root"):
    db_path = project_root / Path(raw_db_path.replace("$project_root", "").lstrip(r"/\\"))
else:
    db_path = Path(raw_db_path)

print(f"Using database path: {db_path}")

# Path to your validated symbols YAML
VALIDATED_SYMBOLS_PATH = project_root / "stock-symbol-analyzer/data" / "validated_symbols.yaml"

print(f"Using validated symbols path: {VALIDATED_SYMBOLS_PATH}")

def create_symbols_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS symbols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol VARCHAR(10) NOT NULL UNIQUE,
        name VARCHAR(255),
        sector VARCHAR(100),
        industry VARCHAR(100),
        country VARCHAR(100),
        market_cap VARCHAR(20),
        exchange VARCHAR(20),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn.execute(create_table_sql)
    conn.commit()

def load_validated_symbols():
    with open(VALIDATED_SYMBOLS_PATH, "r") as f:
        data = yaml.safe_load(f)
    print("First symbol loaded:", data.get("valid_symbols", [])[0])
    return data.get("valid_symbols", [])

def insert_symbols(conn, symbols):
    insert_sql = """
    INSERT OR REPLACE INTO symbols (symbol, name, sector, industry, country, market_cap, exchange)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    for s in symbols:
        print(f"Inserting: {s['symbol']} | name: {s.get('name')}")
        conn.execute(
            insert_sql,
            (
                s["symbol"],
                s.get("name", None),
                s.get("sector", None),
                s.get("industry", None),
                s.get("country", None),
                str(s.get("market_cap", "")),
                s.get("exchange", None),
            ),
        )
    conn.commit()

def main():
    conn = sqlite3.connect(str(db_path))
    create_symbols_table(conn)
    symbols = load_validated_symbols()
    insert_symbols(conn, symbols)
    print(f"Inserted {len(symbols)} symbols into the database at {db_path}.")
    conn.close()

if __name__ == "__main__":
    main()
