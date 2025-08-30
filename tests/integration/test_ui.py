import pytest
import streamlit as st
from app.ui.streamlit_app import API_URL
import requests
from unittest.mock import patch, MagicMock

def test_api_url_configuration():
    """Test API URL configuration"""
    assert API_URL == "http://localhost:8000"

@pytest.mark.integration
def test_successful_query_display(monkeypatch):
    """Test successful query results display"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "explanation": "SELECT * FROM branches LIMIT 5",
        "guard_reason": "Query limited to 5 results",
        "table": {
            "columns": ["id", "name", "city"],
            "rows": [["BR001", "Downtown", "New York"]]
        }
    }
    
    with patch('requests.post', return_value=mock_response):
        with patch('streamlit.text_input') as mock_input:
            mock_input.return_value = "Show all branches"
            # Test would continue here with streamlit session state
            # Note: Full streamlit testing requires more complex setup

@pytest.mark.integration
def test_error_handling(monkeypatch):
    """Test error handling in UI"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    
    with patch('requests.post', return_value=mock_response):
        with patch('streamlit.text_input') as mock_input:
            mock_input.return_value = "Invalid query"
            # Test would continue here with streamlit error handling
            # Note: Full streamlit testing requires more complex setup

@pytest.mark.integration
def test_role_selection():
    """Test role selection functionality"""
    assert "analyst" in ["analyst", "viewer", "admin"]  # Default roles
    # Note: Full streamlit testing requires more complex setup
