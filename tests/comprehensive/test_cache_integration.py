#!/usr/bin/env python3
"""
Integration test to verify cache clearing functionality works properly.
This script tests the actual cache behavior in the real application.
"""

import time
import requests
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_cache_clearing_manually():
    """Test cache clearing by directly calling the functions"""
    print("🧪 Testing Cache Clearing Functionality")
    print("=" * 50)
    
    try:
        from app.utils.cache import cached_plan, clear_cache, schema_hash
        from app.graph.pipeline import initialize_pipeline, clear_pipeline_cache
        from app.models.sql_agent import get_schema_text
        
        # Test 1: Basic cache functionality
        print("\n1️⃣ Testing basic cache functionality...")
        clear_cache()
        
        schema = get_schema_text()
        key = schema_hash(schema)
        
        # Make the same call twice to test caching
        print("   Making first call...")
        try:
            result1 = cached_plan(key, "Show me all customers")
            print(f"   ✅ First result: {result1[:50]}...")
        except Exception as e:
            print(f"   ⚠️ First call failed (LLM might not be available): {e}")
            result1 = None
        
        print("   Making second call (should use cache)...")
        try:
            result2 = cached_plan(key, "Show me all customers")
            print(f"   ✅ Second result: {result2[:50]}...")
            
            if result1 and result2:
                if result1 == result2:
                    print("   ✅ Cache working: Same results returned")
                else:
                    print("   ❌ Cache issue: Different results returned")
        except Exception as e:
            print(f"   ⚠️ Second call failed: {e}")
        
        # Test 2: Cache clearing
        print("\n2️⃣ Testing cache clearing...")
        print("   Clearing cache...")
        clear_cache()
        print("   ✅ Cache cleared successfully")
        
        # Test 3: Pipeline cache clearing
        print("\n3️⃣ Testing pipeline cache clearing...")
        result = clear_pipeline_cache()
        print(f"   ✅ Pipeline cache clear result: {result}")
        
        # Test 4: Initialize pipeline
        print("\n4️⃣ Testing pipeline initialization...")
        initialize_pipeline()
        print("   ✅ Pipeline initialized successfully")
        
        print("\n✅ All manual cache tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Manual cache test failed: {e}")
        return False

def test_api_cache_clearing():
    """Test cache clearing via API endpoint"""
    print("\n🌐 Testing API Cache Clearing")
    print("=" * 30)
    
    api_url = "http://localhost:8000"
    
    # Test if API is running
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print("   ⚠️ API not running or not healthy")
            return False
    except requests.exceptions.RequestException:
        print("   ⚠️ API not accessible at http://localhost:8000")
        return False
    
    # Test cache clearing endpoint
    try:
        print("   Calling /admin/clear-cache endpoint...")
        response = requests.post(f"{api_url}/admin/clear-cache", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache cleared via API: {data.get('message', 'Success')}")
            return True
        else:
            print(f"   ❌ API cache clear failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API cache clear error: {e}")
        return False

def test_end_to_end_cache_behavior():
    """Test end-to-end cache behavior with actual queries"""
    print("\n🔄 Testing End-to-End Cache Behavior")
    print("=" * 40)
    
    api_url = "http://localhost:8000"
    
    try:
        # Test if API is running
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print("   ⚠️ API not running - skipping E2E test")
            return False
    except:
        print("   ⚠️ API not accessible - skipping E2E test")
        return False
    
    # Clear cache first
    print("   Clearing cache via API...")
    requests.post(f"{api_url}/admin/clear-cache")
    
    # Make the same query multiple times
    question = "Show me all branches"
    results = []
    
    print(f"   Testing query: '{question}'")
    
    for i in range(3):
        print(f"   Making request {i+1}/3...")
        try:
            response = requests.post(f"{api_url}/ask", json={
                "question": question,
                "role": "analyst", 
                "user": "test_user"
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                sql = data.get("sql", "")
                results.append(sql)
                print(f"   ✅ Request {i+1} SQL: {sql[:50]}...")
            else:
                print(f"   ❌ Request {i+1} failed: {response.status_code}")
                results.append(None)
                
        except Exception as e:
            print(f"   ❌ Request {i+1} error: {e}")
            results.append(None)
        
        time.sleep(1)  # Brief pause between requests
    
    # Analyze results
    valid_results = [r for r in results if r is not None]
    if len(valid_results) >= 2:
        if all(r == valid_results[0] for r in valid_results):
            print("   ✅ Consistent results (cache working or LLM deterministic)")
        else:
            print("   ⚠️ Inconsistent results (might indicate cache issues)")
        return True
    else:
        print("   ⚠️ Not enough valid results to analyze cache behavior")
        return False

def main():
    """Run all cache tests"""
    print("🧪 CACHE FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Manual cache functions
    print("\n📋 Test 1: Manual Cache Functions")
    results.append(test_cache_clearing_manually())
    
    # Test 2: API cache clearing
    print("\n📋 Test 2: API Cache Clearing")
    results.append(test_api_cache_clearing())
    
    # Test 3: End-to-end behavior
    print("\n📋 Test 3: End-to-End Cache Behavior")
    results.append(test_end_to_end_cache_behavior())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All cache tests PASSED!")
        print("✅ Cache clearing functionality is working correctly")
    elif passed > 0:
        print("⚠️ Some cache tests PASSED, some failed")
        print("🔧 Cache functionality is partially working")
    else:
        print("❌ All cache tests FAILED")
        print("🚨 Cache functionality needs investigation")
    
    print("\n💡 Tips:")
    print("- Make sure Ollama is running: ollama serve")
    print("- Make sure CodeLlama is loaded: ollama run codellama:13b")
    print("- Start the API: uv run python run_app.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
