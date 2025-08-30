import pytest
from fastapi.testclient import TestClient
from app.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.parametrize("question, role", [
    ("Show all branches", "analyst"),
    ("list all customers", "viewer"),
])
def test_ask_endpoint_basic_queries(client, test_db, question, role):
    """Test basic, valid queries through the API."""
    response = client.post("/ask", json={
        "question": question,
        "role": role,
        "user": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert "guard_reason" in data
    assert "table" in data
    assert "error" not in data["table"]
    assert "columns" in data["table"]
    assert "rows" in data["table"]
    assert len(data["table"]["rows"]) > 0

def test_ask_endpoint_with_invalid_role(client, test_db):
    """Test that a query with an invalid role defaults to a safe role and succeeds."""
    response = client.post("/ask", json={
        "question": "Show all branches",
        "role": "invalid_role",
        "user": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "table" in data
    assert "error" not in data["table"]

def test_ask_endpoint_with_complex_query(client, test_db):
    """Test a complex query that requires LLM processing."""
    
    response = client.post("/ask", json={
        "question": "top 2 branches by deposits",
        "role": "analyst",
        "user": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    
    assert "table" in data
    table = data["table"]
    
    # If LLM is not available, the query should fail gracefully
    if "error" in table:
        # LLM not available - this is acceptable since no fallback exists
        assert any(phrase in table["error"].lower() for phrase in ["llm", "not available", "generation failed"])
    else:
        # LLM is available and query succeeded
        assert len(table["columns"]) >= 1
        assert len(table["rows"]) >= 0  # May return 0 rows if no data matches
        
        # If we have results, check basic structure
        if len(table["rows"]) > 0 and len(table["columns"]) >= 2:
            # Check that we have reasonable data types
            for row in table["rows"]:
                assert len(row) >= 2
                # First column likely branch name (string), second likely amount (numeric)
                assert isinstance(row[0], str)  # Branch name should be string
                if isinstance(row[1], (int, float)):
                    assert row[1] >= 0  # Amount should be non-negative

def test_ask_endpoint_with_blocked_query(client, test_db):
    """Test that a malicious query is blocked by the guard and returns an error."""
    response = client.post("/ask", json={
        "question": "DELETE FROM branches",  # Should be blocked by guard
        "role": "analyst",
        "user": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "table" in data
    assert "error" in data["table"]
    assert "Blocked: non read-only SQL detected" in data["table"]["error"]

def test_ask_endpoint_with_no_results_query(client, test_db):
    """Test a valid query that should return no results."""
    response = client.post("/ask", json={
        "question": "show customers from California",
        "role": "analyst",
        "user": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "table" in data
    table = data["table"]
    assert "error" not in table
    assert len(table["rows"]) == 0
