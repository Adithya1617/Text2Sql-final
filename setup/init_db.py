import sqlite3, pathlib, datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
DB_PATH = BASE / "app" / "data.db"
SCHEMA_SQL = BASE / "banking_schema_sqlite.sql"
DATA_SQL = BASE / "banking_data.sql"

def run_sql_file(conn, path: pathlib.Path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)

def ensure_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if SCHEMA_SQL.exists() and DATA_SQL.exists():
        print("Loading provided schema and data...")
        run_sql_file(conn, SCHEMA_SQL)
        run_sql_file(conn, DATA_SQL)
    else:
        print("Provided SQL not found — creating minimal demo schema.")
        cur.executescript("""PRAGMA journal_mode = WAL;
        CREATE TABLE merchants (merchant_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE transactions (txn_id INTEGER PRIMARY KEY, merchant_id INTEGER, amount_cents INTEGER, txn_ts TEXT, card_last4 TEXT);
        """)
        cur.executemany("INSERT INTO merchants(name) VALUES (?)", [("Acme",), ("Globex",)])

    # Create logs table
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        role TEXT,
        question TEXT,
        raw_sql TEXT,
        safe_sql TEXT,
        status TEXT,
        ts TEXT
    );
    """)

    # Create a viewer-safe customers view if customers table exists
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
        if cur.fetchone():
            cur.executescript("""
            DROP VIEW IF EXISTS viewer_customers;
            CREATE VIEW viewer_customers AS
                SELECT id,
                       first_name,
                       last_name,
                       email,
                       'XXXX-XXXX-' || substr(national_id, -4, 4) AS national_id,
                       branch_id
                FROM customers;
            """)
    except Exception:
        pass

    conn.commit()
    conn.close()
    print(f"Initialized DB at {DB_PATH}")

if __name__ == "__main__":
    ensure_db()
