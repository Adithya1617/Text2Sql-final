from functools import lru_cache
import hashlib

def schema_hash(schema_text: str) -> str:
    return hashlib.sha256(schema_text.encode('utf-8')).hexdigest()

@lru_cache(maxsize=512)
def cached_plan(schema_h: str, question: str):
    from ..models.sql_agent import question_to_sql
    return question_to_sql(question)

def clear_cache():
    """Clear the LRU cache to force fresh SQL generation"""
    cached_plan.cache_clear()
    print("✅ Cache cleared!")
