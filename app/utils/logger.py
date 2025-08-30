import logging, sys
from datetime import datetime

def get_logger(name: str = "app"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger

def log_event(user, role, question, raw_sql, safe_sql, status="ok"):
    log_entry = {
        "user": user,
        "role": role,
        "question": question,
        "raw_sql": raw_sql,
        "safe_sql": safe_sql,
        "status": status,

        "ts": datetime.utcnow().isoformat()
    }
    ...
