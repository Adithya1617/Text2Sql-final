from .nodes import Intent, Plan, GuardedSQL, ExecutionResult
from ..models.sql_agent import question_to_sql, get_schema_text
try:
    # Optional guided re-ask if initial SQL is irrelevant
    from ..models.sql_agent import question_to_sql_with_guidance as _guided_ask
except Exception:
    _guided_ask = None
from ..guards.sql_guard import enforce_read_only_and_limit
from ..executors.sqlite_exec import run_sql
from ..utils.audit import log_query
from ..utils.logger import get_logger
from ..utils import cache as cache_utils

def initialize_pipeline():
    """Initialize the pipeline and clear any cached data from previous runs"""
    print("🔄 Initializing pipeline...")
    cache_utils.clear_cache()
    print("✅ Pipeline initialized with fresh cache")

def clear_pipeline_cache():
    """Clear the pipeline cache manually"""
    cache_utils.clear_cache()
    return {"status": "success", "message": "Pipeline cache cleared"}

def parse_intent(question: str) -> Intent:
    return Intent(raw=question, parsed={})

def plan_query(intent: Intent) -> Plan:
    return Plan(steps=["generate_sql", "guard", "execute", "postprocess"])

def generate_sql(plan: Plan, question: str) -> Plan:
    schema_txt = get_schema_text()
    key = cache_utils.schema_hash(schema_txt)
    try:
        sql = cache_utils.cached_plan(key, question)
    except Exception:
        sql = question_to_sql(question)
    # Improved SQL cleaning logic
    if sql:
        # Remove common LLM artifacts
        sql = sql.replace("SQLResult:", "").replace("```sql", "").replace("```", "").replace('"""', '').strip()
        
        # Handle multiple statements more carefully
        if ";" in sql:
            # Split by semicolon and take the first valid statement
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            if statements:
                sql = statements[0]
        
        # Basic SQL validation
        if not sql.lower().startswith("select"):
            raise ValueError("Generated SQL must start with SELECT")
        
        # Remove any trailing semicolons
        sql = sql.rstrip(";").strip()
        
        # Ensure SQL is not empty
        if not sql:
            raise ValueError("Generated SQL is empty")

        # Detect degenerate generic SQL patterns and trigger a guided re-ask
        sql_lower_full = sql.lower().strip().rstrip(";")
        degenerate_candidates = [
            "select t.id, t.amount, t.type, t.transaction_date from transactions t order by t.transaction_date desc limit 25",
        ]
        if _guided_ask is not None and any(sql_lower_full == p for p in degenerate_candidates):
            try:
                anti_pattern_guidance = "\n".join([
                    "Do NOT return the generic 'latest transactions' query.",
                    "Answer the user's question using only relevant tables and attributes.",
                    "Avoid using transactions unless explicitly requested by the question.",
                ])
                guided_sql0 = _guided_ask(question, anti_pattern_guidance)
                if guided_sql0 and guided_sql0.strip().lower().startswith("select"):
                    sql = guided_sql0.strip().rstrip(";")
                    try:
                        cache_utils.clear_cache()
                    except Exception:
                        pass
            except Exception:
                pass

        # Relevance guard: if question doesn't mention transactions but SQL uses transactions, try guided re-ask once
        q_lower = question.lower()
        uses_transactions = " from transactions" in sql.lower() or " join transactions" in sql.lower()
        mentions_transactions = any(word in q_lower for word in ["transaction", "transactions", "transaction_date", "weekend", "today", "recent"])
        if uses_transactions and not mentions_transactions and _guided_ask is not None:
            try:
                guidance_lines = [
                    "Do NOT use the transactions table unless explicitly asked.",
                    "Use customers (c) and accounts (a) tables to compute counts per customer attributes.",
                    "For 'accounts per gender', join customers c to accounts a on a.customer_id = c.id, then GROUP BY c.gender and COUNT(a.id).",
                    "Return a single SELECT with GROUP BY, and ORDER BY count descending when appropriate.",
                ]
                guided_sql = _guided_ask(question, "\n".join(guidance_lines))
                if guided_sql and guided_sql.strip().lower().startswith("select"):
                    sql = guided_sql.strip().rstrip(";")
                    # Clear cache so subsequent calls don't return the previous irrelevant cached SQL
                    try:
                        cache_utils.clear_cache()
                    except Exception:
                        pass
            except Exception:
                # Ignore guided re-ask failure and keep original sql
                pass

        # Additional intent consistency checks and guided correction
        if _guided_ask is not None:
            sql_lower = sql.lower()
            guidance = []
            # If question mentions withdrawal but SQL doesn't, enforce it
            if ("withdrawal" in q_lower) and ("withdrawal" not in sql_lower):
                guidance.append("When question references withdrawals, include a predicate or CASE using t.type = 'withdrawal'.")
            # If question implies 'never had' withdrawals, suggest anti-join pattern
            if ("never" in q_lower and "withdrawal" in q_lower):
                guidance.append("Return accounts with zero withdrawals using LEFT JOIN transactions t ON a.id = t.account_id AND t.type = 'withdrawal' and filter WHERE t.id IS NULL, or use NOT EXISTS.")
            # If question implies grouping (per/each) but SQL lacks GROUP BY
            if (" per " in q_lower or " for each" in q_lower or "each " in q_lower) and ("group by" not in sql_lower):
                guidance.append("Use GROUP BY on the attribute being summarized and appropriate aggregates like COUNT().")
            # Avoid ordering by transaction_date unless explicitly requested
            if ("order by transaction_date" in sql_lower) and not any(w in q_lower for w in ["latest", "recent", "today", "weekend", "last", "newest"]):
                guidance.append("Do NOT ORDER BY transaction_date unless the question asks for recency; prefer ORDER BY aggregate when relevant.")

            if guidance:
                try:
                    guided_sql2 = _guided_ask(question, "\n".join(guidance))
                    if guided_sql2 and guided_sql2.strip().lower().startswith("select"):
                        sql = guided_sql2.strip().rstrip(";")
                        try:
                            cache_utils.clear_cache()
                        except Exception:
                            pass
                except Exception:
                    pass
    
    plan.sql = sql
    return plan

def guard_sql(plan: Plan, role: str = "analyst") -> GuardedSQL:
    table_map = {}
    if role == "viewer":
        table_map = {"customers": "viewer_customers"}
    safe_sql, reason = enforce_read_only_and_limit(plan.sql, default_limit=200, role=role, table_mapping=table_map)
    return GuardedSQL(sql=safe_sql, reason=reason)

def execute_sql(guarded: GuardedSQL):
    return run_sql(guarded.sql)

def postprocess(table: dict, role: str = "analyst"):
    return table

def run_pipeline(question: str, role: str = "analyst", user: str = "anonymous"):
    logger = get_logger("pipeline")
    logger.info(f"🎯 Starting pipeline for user={user}, role={role}")
    logger.info(f"📝 Question: {question}")
    
    intent = parse_intent(question)
    plan = plan_query(intent)
    
    try:
        logger.info(f"🤖 Generating SQL for question: '{question[:120]}'")
        plan = generate_sql(plan, question)
        logger.info(f"✅ SQL generation completed: {len(plan.sql) if plan.sql else 0} chars")
    except ValueError as e:
        # SQL generation failed - return error table
        table = {
            "columns": [],
            "rows": [],
            "error": f"SQL Generation failed: {str(e)}",
            "elapsed_sec": 0.0
        }
        guarded = GuardedSQL(sql="", reason=f"SQL Generation failed: {str(e)}")
        return {
            "intent": intent.raw,
            "sql": "",
            "safe_sql": "",
            "guard_reason": f"SQL Generation failed: {str(e)}",
            "table": table,
        }
    except Exception as e:
        # Other SQL generation errors
        table = {
            "columns": [],
            "rows": [],
            "error": f"Unexpected error during SQL generation: {str(e)}",
            "elapsed_sec": 0.0
        }
        guarded = GuardedSQL(sql="", reason=f"Unexpected error: {str(e)}")
        return {
            "intent": intent.raw,
            "sql": "",
            "safe_sql": "",
            "guard_reason": f"Unexpected error: {str(e)}",
            "table": table,
        }
    
    try:
        logger.info("🛡️ Guarding SQL and executing")
        guarded = guard_sql(plan, role=role)
        logger.info(f"🔒 Guard result: {guarded.reason[:100] if guarded.reason else 'OK'}")
        
        logger.info("⚡ Executing SQL query")
        result = execute_sql(guarded)
        logger.info(f"📊 Execution result: {len(result.get('rows', []))} rows, {result.get('elapsed_sec', 0):.3f}s")
        
        table = postprocess(result, role=role)
    except ValueError as e:
        # Guard validation failed - return error table
        table = {
            "columns": [],
            "rows": [],
            "error": f"Security validation failed: {str(e)}",
            "elapsed_sec": 0.0
        }
        guarded = GuardedSQL(sql="", reason=f"Guard failed: {str(e)}")
    except Exception as e:
        # Other execution errors
        table = {
            "columns": [],
            "rows": [],
            "error": f"Query execution failed: {str(e)}",
            "elapsed_sec": 0.0
        }
        guarded = GuardedSQL(sql="", reason=f"Execution failed: {str(e)}")

    try:
        raw_sql = plan.sql
        safe_sql = guarded.sql if hasattr(guarded, "sql") else ""
        status = "ok" if not table.get("error") else "error"
        log_query(user=user, role=role, question=question, raw_sql=raw_sql, safe_sql=safe_sql, status=status)
    except Exception:
        pass

    return {
        "intent": intent.raw,
        "sql": plan.sql,
        "safe_sql": guarded.sql,
        "guard_reason": guarded.reason,
        "table": table,
    }
