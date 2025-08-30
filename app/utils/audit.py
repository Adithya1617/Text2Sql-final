import sqlite3, pathlib, datetime

DB_PATH = pathlib.Path(__file__).resolve().parents[1] / "data.db"

def log_query(user: str, role: str, question: str, raw_sql: str, safe_sql: str, status: str = "ok"):
    ts = datetime.datetime.utcnow().isoformat()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO logs(user, role, question, raw_sql, safe_sql, status, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user, role, question, raw_sql, safe_sql, status, ts),
            )
            conn.commit()
    except Exception as e:
        print("Audit log error:", e)
