import pytest
from unittest.mock import patch, MagicMock
from app.utils.cache import cached_plan, clear_cache, schema_hash
from app.graph.pipeline import initialize_pipeline, clear_pipeline_cache


def test_cache_basic_functionality():
    """Test that cache stores and retrieves values correctly"""
    # Clear cache first
    clear_cache()
    
    # Mock the question_to_sql function to return predictable results
    with patch('app.models.sql_agent.question_to_sql') as mock_sql:
        mock_sql.return_value = "SELECT * FROM customers"
        
        # First call should invoke the function
        result1 = cached_plan("test_schema", "test question")
        assert result1 == "SELECT * FROM customers"
        assert mock_sql.call_count == 1
        
        # Second call with same parameters should use cache (no additional call)
        result2 = cached_plan("test_schema", "test question")
        assert result2 == "SELECT * FROM customers"
        assert mock_sql.call_count == 1  # Still 1, proving cache was used


def test_cache_clearing():
    """Test that cache clearing forces fresh calls"""
    # Clear cache first
    clear_cache()
    
    with patch('app.models.sql_agent.question_to_sql') as mock_sql:
        mock_sql.side_effect = ["SQL1", "SQL2", "SQL3"]  # Different responses
        
        # First call
        result1 = cached_plan("test_schema", "test question")
        assert result1 == "SQL1"
        assert mock_sql.call_count == 1
        
        # Second call should use cache
        result2 = cached_plan("test_schema", "test question")
        assert result2 == "SQL1"  # Same result from cache
        assert mock_sql.call_count == 1  # No new call
        
        # Clear cache
        clear_cache()
        
        # Third call should invoke function again after cache clear
        result3 = cached_plan("test_schema", "test question")
        assert result3 == "SQL2"  # New result
        assert mock_sql.call_count == 2  # New call made


def test_pipeline_cache_clearing():
    """Test pipeline cache clearing functions"""
    # Test initialize_pipeline clears cache
    with patch('app.utils.cache.clear_cache') as mock_clear:
        initialize_pipeline()
        mock_clear.assert_called_once()
    
    # Test clear_pipeline_cache function
    with patch('app.utils.cache.clear_cache') as mock_clear:
        result = clear_pipeline_cache()
        mock_clear.assert_called_once()
        assert result["status"] == "success"
        assert "cleared" in result["message"]


def test_different_questions_different_cache():
    """Test that different questions create different cache entries"""
    clear_cache()
    
    with patch('app.models.sql_agent.question_to_sql') as mock_sql:
        mock_sql.side_effect = ["SQL for customers", "SQL for branches"]
        
        # Different questions should call the function separately
        result1 = cached_plan("schema", "show customers")
        result2 = cached_plan("schema", "show branches")
        
        assert result1 == "SQL for customers"
        assert result2 == "SQL for branches"
        assert mock_sql.call_count == 2  # Two separate calls


def test_different_schemas_different_cache():
    """Test that different schemas create different cache entries"""
    clear_cache()
    
    with patch('app.models.sql_agent.question_to_sql') as mock_sql:
        mock_sql.side_effect = ["SQL for schema1", "SQL for schema2"]
        
        # Same question but different schemas should call function separately
        result1 = cached_plan("schema1", "show data")
        result2 = cached_plan("schema2", "show data")
        
        assert result1 == "SQL for schema1"
        assert result2 == "SQL for schema2"
        assert mock_sql.call_count == 2  # Two separate calls


def test_schema_hash_consistency():
    """Test that schema hash produces consistent results"""
    schema1 = "CREATE TABLE test (id INT)"
    schema2 = "CREATE TABLE test (id INT)"
    schema3 = "CREATE TABLE different (id INT)"
    
    hash1 = schema_hash(schema1)
    hash2 = schema_hash(schema2)
    hash3 = schema_hash(schema3)
    
    assert hash1 == hash2  # Same schema should produce same hash
    assert hash1 != hash3  # Different schema should produce different hash
    assert len(hash1) == 64  # SHA256 hash should be 64 characters


def test_cache_with_exceptions():
    """Test cache behavior when underlying function raises exceptions"""
    clear_cache()
    
    with patch('app.models.sql_agent.question_to_sql') as mock_sql:
        mock_sql.side_effect = Exception("LLM not available")
        
        # Exception should be raised and not cached
        with pytest.raises(Exception, match="LLM not available"):
            cached_plan("schema", "test question")
        
        # Second call should also raise exception (not cached)
        with pytest.raises(Exception, match="LLM not available"):
            cached_plan("schema", "test question")
        
        assert mock_sql.call_count == 2  # Function called twice, no caching of exceptions
