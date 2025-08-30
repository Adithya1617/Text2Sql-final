import pytest
from app.guards.sql_guard import enforce_read_only_and_limit

def test_read_only_enforcement():
    """Test that non-SELECT (i.e., mutating) statements are blocked."""
    # Test INSERT
    with pytest.raises(ValueError, match="Blocked: non read-only SQL detected"):
        enforce_read_only_and_limit("INSERT INTO branches VALUES (1, 'test')")
    
    # Test UPDATE
    with pytest.raises(ValueError, match="Blocked: non read-only SQL detected"):
        enforce_read_only_and_limit("UPDATE branches SET name = 'test'")
    
    # Test DELETE
    with pytest.raises(ValueError, match="Blocked: non read-only SQL detected"):
        enforce_read_only_and_limit("DELETE FROM branches")

def test_limit_enforcement():
    """Test that a LIMIT clause is correctly added or adjusted."""
    # Test query without LIMIT gets a LIMIT added
    sql_no_limit = "SELECT * FROM branches"
    safe_sql_no_limit, reason = enforce_read_only_and_limit(sql_no_limit)
    assert "LIMIT 100" in safe_sql_no_limit.upper()
    assert "LIMIT injected" in reason
    
    # Test query with an existing, compliant LIMIT is unchanged
    sql_with_limit = "SELECT * FROM branches LIMIT 5"
    safe_sql_with_limit, reason = enforce_read_only_and_limit(sql_with_limit)
    assert "LIMIT 5" in safe_sql_with_limit.upper()
    assert reason == "OK"
    
    # Test that a high LIMIT is reduced to the maximum allowed
    sql_high_limit = "SELECT * FROM branches LIMIT 5000"
    safe_sql_high_limit, reason = enforce_read_only_and_limit(sql_high_limit, default_limit=1000)
    assert "LIMIT 1000" in safe_sql_high_limit.upper()
    assert "LIMIT reduced" in reason

def test_block_potentially_malicious_queries():
    """Test that common SQL injection and malicious patterns are blocked."""
    
    # Test blocking multiple statements, which could hide a malicious command.
    # This is often caught by parsers that expect a single statement.
    with pytest.raises(ValueError, match="Only single SELECT statements are allowed"):
        enforce_read_only_and_limit("SELECT * FROM branches; SELECT * FROM customers")
    
    # Test blocking access to system tables like sqlite_master, which can be
    # used to exfiltrate database schema information.
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        enforce_read_only_and_limit("SELECT * FROM branches UNION SELECT * FROM sqlite_master")
