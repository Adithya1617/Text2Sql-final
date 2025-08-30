#!/usr/bin/env python3
"""
Comprehensive LLM Integration Test
Tests if Ollama and the LLM model are working properly with the backend.
"""

import requests
import time
import sys
import os

# Add app to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_ollama_server():
    """Test if Ollama server is running"""
    print("🔍 Testing Ollama Server Connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"   ✅ Ollama server is running")
            print(f"   📋 Available models: {len(models)}")
            
            # Check if our target model is available
            target_model = "hf.co/defog/sqlcoder-7b-2:latest"
            model_names = [model.get("name", "") for model in models]
            
            if target_model in model_names:
                print(f"   ✅ Target model '{target_model}' is available")
                return True, target_model
            else:
                print(f"   ⚠️ Target model '{target_model}' not found")
                print(f"   📝 Available models: {model_names}")
                return False, target_model
        else:
            print(f"   ❌ Ollama server returned status {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Ollama server at localhost:11434")
        print("   💡 Start with: ollama serve")
        return False, None
    except Exception as e:
        print(f"   ❌ Error checking Ollama: {e}")
        return False, None

def test_ollama_model_direct(model_name):
    """Test the model directly via Ollama API"""
    print(f"\n🤖 Testing Model '{model_name}' Directly...")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "Generate only this SQL: SELECT 1 as test",
            "stream": False,
            "options": {
                "num_ctx": 1024,
                "temperature": 0
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "").strip()
            print(f"   ✅ Model responded successfully")
            print(f"   📝 Response: {response_text[:100]}...")
            print(f"   ⏱️ Done: {data.get('done', False)}")
            return True, response_text
        else:
            print(f"   ❌ Model request failed with status {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Error testing model: {e}")
        return False, None

def test_backend_health():
    """Test if the backend is running and healthy"""
    print("\n🏥 Testing Backend Health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend is running")
            print(f"   📊 Status: {data.get('status', 'unknown')}")
            
            services = data.get("services", {})
            for service, status in services.items():
                emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"   {emoji} {service}: {status}")
            
            return True, data
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend at localhost:8000")
        print("   💡 Start with: uv run python run_app.py")
        return False, None
    except Exception as e:
        print(f"   ❌ Error checking backend health: {e}")
        return False, None

def test_llm_via_backend():
    """Test LLM integration through the backend API"""
    print("\n🔗 Testing LLM Integration via Backend API...")
    
    test_questions = [
        "SELECT 1 as one",
        "Show all customers",
        "Find the total number of accounts"
    ]
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"   🧪 Test {i}: '{question}'")
        
        try:
            payload = {
                "question": question,
                "role": "analyst",
                "user": "llm_test_user"
            }
            
            response = requests.post(
                "http://localhost:8000/ask",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                sql = data.get("explanation", "")
                table = data.get("table", {})
                error = table.get("error", "")
                
                if success and sql and not error:
                    print(f"      ✅ Success: {sql[:60]}...")
                    results.append(True)
                else:
                    print(f"      ❌ Failed: {error or 'No SQL generated'}")
                    results.append(False)
                    
            else:
                print(f"      ❌ API error: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"      ❌ Request error: {e}")
            results.append(False)
        
        time.sleep(1)  # Brief pause between requests
    
    success_rate = sum(results) / len(results) if results else 0
    print(f"\n   📊 Success rate: {len([r for r in results if r])}/{len(results)} ({success_rate:.1%})")
    
    return success_rate > 0.5, results

def test_cache_clearing():
    """Test cache clearing functionality"""
    print("\n🗑️ Testing Cache Clearing...")
    
    try:
        response = requests.post("http://localhost:8000/admin/clear-cache", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache cleared successfully")
            print(f"   📝 Message: {data.get('message', 'No message')}")
            return True
        else:
            print(f"   ❌ Cache clear failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error clearing cache: {e}")
        return False

def main():
    """Run comprehensive LLM integration test"""
    print("🎯 LLM INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Ollama Server
    print("\n📋 Test 1: Ollama Server")
    ollama_ok, model_name = test_ollama_server()
    results.append(ollama_ok)
    
    # Test 2: Model Direct (if Ollama is working)
    if ollama_ok and model_name:
        print("\n📋 Test 2: Model Direct Test")
        model_ok, _ = test_ollama_model_direct(model_name)
        results.append(model_ok)
    else:
        print("\n📋 Test 2: Model Direct Test - SKIPPED (Ollama not available)")
        results.append(False)
    
    # Test 3: Backend Health
    print("\n📋 Test 3: Backend Health")
    backend_ok, _ = test_backend_health()
    results.append(backend_ok)
    
    # Test 4: LLM via Backend (if backend is working)
    if backend_ok:
        print("\n📋 Test 4: LLM Integration via Backend")
        llm_backend_ok, _ = test_llm_via_backend()
        results.append(llm_backend_ok)
    else:
        print("\n📋 Test 4: LLM Integration via Backend - SKIPPED (Backend not available)")
        results.append(False)
    
    # Test 5: Cache Clearing (if backend is working)
    if backend_ok:
        print("\n📋 Test 5: Cache Clearing")
        cache_ok = test_cache_clearing()
        results.append(cache_ok)
    else:
        print("\n📋 Test 5: Cache Clearing - SKIPPED (Backend not available)")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Ollama Server",
        "Model Direct",
        "Backend Health", 
        "LLM via Backend",
        "Cache Clearing"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! LLM integration is working perfectly.")
    elif passed >= 3:
        print("⚠️ MOST TESTS PASSED. LLM integration is mostly working.")
    else:
        print("❌ MANY TESTS FAILED. LLM integration needs attention.")
    
    print("\n💡 Next Steps:")
    if not results[0]:  # Ollama server
        print("- Start Ollama: ollama serve")
        print("- Pull model: ollama pull sqlcoder7b:latest")
    if not results[2]:  # Backend
        print("- Start backend: uv run python run_app.py")
    if results[2] and not results[3]:  # Backend ok but LLM integration fails
        print("- Check LLM logs in backend console")
        print("- Verify model is loaded in Ollama")
        print("- Clear cache: curl -X POST http://localhost:8000/admin/clear-cache")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
