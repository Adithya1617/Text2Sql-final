import re
from typing import Tuple, Dict
from sqlglot import parse
from sqlglot.expressions import Select
import sqlite3, pathlib
from ..utils.logger import get_logger

logger = get_logger("sql_guard")

FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH)\b", re.I)

BASE = pathlib.Path(__file__).resolve().parents[1]
DB_PATH = BASE / "data.db"

def _get_schema_columns() -> Dict[str, set]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]
    schema = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = {r[1] for r in cur.fetchall()}
        schema[t] = cols
    conn.close()
    return schema

def _qualify_unqualified_columns(sql: str, schema_cols: Dict[str, set]) -> str:
    for col in set().union(*schema_cols.values()):
        pattern = rf"(?<![\.\w]){re.escape(col)}(?![\.\w])"
        owners = [t for t, cols in schema_cols.items() if col in cols]
        if len(owners) == 1:
            replacement = f"{owners[0]}.{col}"
            sql = re.sub(pattern, replacement, sql)
    return sql

def enforce_read_only_and_limit(sql: str, default_limit: int = 100, role: str = "analyst", table_mapping: Dict[str,str]=None) -> Tuple[str, str]:
    s = sql.strip().rstrip(";")
    s = s.replace("SQLResult:", "").replace("```sql", "").replace("```", "").replace('"""', '').strip()

    if FORBIDDEN.search(s):
        raise ValueError("Blocked: non read-only SQL detected.")

    if table_mapping:
        for orig, repl in table_mapping.items():
            s = re.sub(rf"\b{orig}\b", repl, s, flags=re.IGNORECASE)

    try:
        exprs = parse(s, read="sqlite")
    except Exception as e:
        logger.error("sqlglot parse error: %s", e)
        raise ValueError(f"Failed to parse SQL: {e}")

    if len(exprs) != 1:
        raise ValueError("Only single SELECT statements are allowed.")

    expr = exprs[0]
    if not isinstance(expr, Select):
        raise ValueError("Only SELECT queries are allowed.")

    schema_cols = _get_schema_columns()
    s = _qualify_unqualified_columns(s, schema_cols)

    if s.lower().startswith("select") and " limit " not in s.lower():
        s = f"{s} LIMIT {default_limit}"
        return s, f"LIMIT injected to cap result size at {default_limit}."
    
    # Check if existing LIMIT exceeds the default limit
    limit_match = re.search(r'LIMIT\s+(\d+)', s, re.IGNORECASE)
    if limit_match:
        current_limit = int(limit_match.group(1))
        if current_limit > default_limit:
            s = re.sub(r'LIMIT\s+\d+', f'LIMIT {default_limit}', s, flags=re.IGNORECASE)
            return s, f"LIMIT reduced from {current_limit} to {default_limit} to cap result size."

    return s, "OK"
