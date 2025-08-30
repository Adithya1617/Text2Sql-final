import pytest
from app.graph.pipeline import parse_intent, plan_query, generate_sql, guard_sql, execute_sql, postprocess
from app.graph.nodes import Intent, Plan, GuardedSQL, ExecutionResult

def test_parse_intent():
    """Test intent parsing"""
    question = "Show all branches"
    intent = parse_intent(question)
    assert isinstance(intent, Intent)
    assert intent.raw == question
    assert isinstance(intent.parsed, dict)

def test_plan_query():
    """Test query planning"""
    intent = Intent(raw="Show all branches", parsed={})
    plan = plan_query(intent)
    assert isinstance(plan, Plan)
    assert "generate_sql" in plan.steps
    assert "guard" in plan.steps
    assert "execute" in plan.steps

def test_guard_sql():
    """Test SQL guarding"""
    plan = Plan(steps=["generate_sql"], sql="SELECT * FROM branches")
    
    # Test analyst role
    guarded_analyst = guard_sql(plan, role="analyst")
    assert isinstance(guarded_analyst, GuardedSQL)
    assert "SELECT" in guarded_analyst.sql.upper()
    
    # Test viewer role
    guarded_viewer = guard_sql(plan, role="viewer")
    assert isinstance(guarded_viewer, GuardedSQL)
    assert "SELECT" in guarded_viewer.sql.upper()

def test_execute_sql(test_db):
    """Test SQL execution"""
    guarded = GuardedSQL(sql="SELECT * FROM branches", reason="ok")
    result = execute_sql(guarded)
    assert result is not None
    assert "columns" in result
    assert "rows" in result
    assert "error" not in result

def test_postprocess():
    """Test result postprocessing"""
    result = {"columns": ["id", "name"], "rows": [["1", "test"]]}
    processed = postprocess(result, role="analyst")
    assert isinstance(processed, dict)
    assert "columns" in processed
    assert "rows" in processed
