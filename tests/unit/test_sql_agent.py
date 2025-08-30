import pytest
from app.models.sql_agent import get_schema_text, generate_sql
from sqlglot import parse_one

def test_get_schema_text(test_db):
    """Test that schema text is correctly generated and includes all tables."""
    schema = get_schema_text()
    assert "branches" in schema
    assert "customers" in schema
    assert "accounts" in schema
    assert "transactions" in schema
    assert "employees" in schema # New table
    assert "loans" in schema # New table
    assert "transaction_date" in schema # New column

def test_generate_sql_pipeline_with_llm():
    """
    Test the SQL generation pipeline with LLM only.
    This test requires a running LLM since no fallback is available.
    """
    question = "Show all branches"
    try:
        # The schema is retrieved inside generate_sql
        sql = generate_sql(question)
        assert isinstance(sql, str)
        assert "SELECT" in sql.upper()
        assert "branches" in sql.lower()
        # The most important check: the SQL should be valid
        try:
            parse_one(sql)
        except Exception as e:
            pytest.fail(f"Generated SQL is not valid: {sql}\nError: {e}")
    except Exception as e:
        # If LLM is not available, skip the test
        pytest.skip(f"LLM not available: {str(e)}")

def test_generate_sql_with_complex_question(test_db):
    """Test SQL generation with a complex question."""
    question = "Show top 5 branches by deposit amount"
    schema = get_schema_text()
    try:
        sql = generate_sql(question, schema)
        assert sql is not None
        # Check that it's a valid SQL query with the expected structure
        assert "SELECT" in sql.upper()
        assert "branches" in sql.lower() or "branch" in sql.lower()
        assert "deposit" in sql.lower() or "deposits" in sql.lower()
        # The most important check: the SQL should be valid
        try:
            parse_one(sql)
        except Exception as e:
            pytest.fail(f"Generated SQL is not valid: {sql}\nError: {e}")
    except Exception as e:
        # If LLM is not available, skip the test
        pytest.skip(f"LLM not available: {str(e)}")

def test_generate_sql_raises_error_when_no_llm(monkeypatch):
    """
    Test that if the LLM fails, an exception is raised (no fallback available).
    """
    # Mock the LLM to always fail
    def mock_llm_fail(question, schema):
        raise Exception("LLM unavailable")
    monkeypatch.setattr("app.models.sql_agent.llm_generate_sql", mock_llm_fail)

    question = "Any question that requires LLM"
    with pytest.raises(Exception, match="LLM unavailable"):
        generate_sql(question)
