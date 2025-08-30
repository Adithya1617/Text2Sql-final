import sqlite3, contextlib, pathlib, time

DB_PATH = pathlib.Path(__file__).resolve().parents[1] / "data.db"

def run_sql(sql: str, timeout_s: float = 3.0):
    if ";" in sql.strip().rstrip(";"):
        return {"columns": [], "rows": [], "elapsed_sec": 0.0, "error": "Multiple statements are not allowed."}

    start = time.time()
    try:
        with contextlib.closing(sqlite3.connect(DB_PATH, timeout=timeout_s)) as conn:
            conn.row_factory = sqlite3.Row
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description] if cur.description else []
    except sqlite3.OperationalError as e:
        # SQL syntax or operational errors
        error_msg = str(e)
        if "syntax error" in error_msg.lower():
            return {"columns": [], "rows": [], "elapsed_sec": round(time.time() - start, 4), 
                   "error": f"SQL Syntax Error: {error_msg}. Please check the generated SQL."}
        else:
            return {"columns": [], "rows": [], "elapsed_sec": round(time.time() - start, 4), 
                   "error": f"SQL Execution Error: {error_msg}"}
    except Exception as e:
        return {"columns": [], "rows": [], "elapsed_sec": round(time.time() - start, 4), "error": str(e)}

    elapsed = time.time() - start
    data = [dict(r) for r in rows]
    return {"columns": cols, "rows": data, "elapsed_sec": round(elapsed, 4)}
