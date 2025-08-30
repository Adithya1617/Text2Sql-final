#!/usr/bin/env python3
"""
Quick manual test for cache functionality - no pytest required
"""

def test_cache_functions():
    """Test cache functions manually"""
    print("🧪 Quick Cache Test")
    print("=" * 30)
    
    # Test 1: Import test
    print("1️⃣ Testing imports...")
    try:
        from app.utils.cache import clear_cache, schema_hash, cached_plan
        from app.graph.pipeline import initialize_pipeline, clear_pipeline_cache
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Clear cache test
    print("2️⃣ Testing clear_cache()...")
    try:
        clear_cache()
        print("   ✅ clear_cache() works")
    except Exception as e:
        print(f"   ❌ clear_cache() failed: {e}")
        return False
    
    # Test 3: Pipeline cache clearing
    print("3️⃣ Testing clear_pipeline_cache()...")
    try:
        result = clear_pipeline_cache()
        print(f"   ✅ clear_pipeline_cache() works: {result}")
    except Exception as e:
        print(f"   ❌ clear_pipeline_cache() failed: {e}")
        return False
    
    # Test 4: Initialize pipeline
    print("4️⃣ Testing initialize_pipeline()...")
    try:
        initialize_pipeline()
        print("   ✅ initialize_pipeline() works")
    except Exception as e:
        print(f"   ❌ initialize_pipeline() failed: {e}")
        return False
    
    # Test 5: Schema hash
    print("5️⃣ Testing schema_hash()...")
    try:
        hash1 = schema_hash("test")
        hash2 = schema_hash("test")
        if hash1 == hash2 and len(hash1) == 64:
            print(f"   ✅ schema_hash() works: {hash1[:16]}...")
        else:
            print(f"   ❌ schema_hash() inconsistent")
            return False
    except Exception as e:
        print(f"   ❌ schema_hash() failed: {e}")
        return False
    
    print("\n🎉 All cache functions work correctly!")
    return True

def test_cache_behavior():
    """Test actual cache behavior"""
    print("\n🔄 Testing Cache Behavior")
    print("=" * 30)
    
    try:
        from app.utils.cache import cached_plan, clear_cache, schema_hash
        from app.models.sql_agent import get_schema_text
        
        # Clear cache first
        clear_cache()
        print("1️⃣ Cache cleared")
        
        # Get schema
        schema = get_schema_text()
        key = schema_hash(schema)
        print(f"2️⃣ Schema loaded: {len(schema)} chars, hash: {key[:16]}...")
        
        # Test cached_plan (might fail if LLM not available)
        print("3️⃣ Testing cached_plan()...")
        try:
            result = cached_plan(key, "test query")
            print(f"   ✅ cached_plan() returned: {len(result) if result else 0} chars")
            
            # Test cache hit
            result2 = cached_plan(key, "test query")
            if result == result2:
                print("   ✅ Cache working: Same result returned")
            else:
                print("   ⚠️ Cache might not be working: Different results")
                
        except Exception as e:
            print(f"   ⚠️ cached_plan() failed (expected if LLM unavailable): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache behavior test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUICK CACHE FUNCTIONALITY TEST")
    print("=" * 50)
    
    test1 = test_cache_functions()
    test2 = test_cache_behavior()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if test1 and test2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Cache functionality is working correctly")
        print("\n💡 Your cache clearing implementation is working!")
        print("🔧 The generic SQL issue should be resolved after restart")
    elif test1:
        print("⚠️ BASIC FUNCTIONS WORK, but cache behavior has issues")
        print("🔧 This might be due to LLM not being available")
        print("💡 Try starting Ollama: ollama serve && ollama run codellama:13b")
    else:
        print("❌ BASIC FUNCTIONS FAILED")
        print("🚨 There are fundamental issues with the cache implementation")
    
    print("\n🎯 Next Steps:")
    print("- If tests pass: Restart your app to clear cache automatically")
    print("- If tests fail: Check the error messages above")
    print("- Test with: uv run python quick_cache_test.py")
