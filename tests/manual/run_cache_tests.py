#!/usr/bin/env python3
"""
Simple test runner for cache functionality.
Runs both unit tests and integration tests.
"""

import subprocess
import sys
import os

def run_unit_tests():
    """Run the unit tests for cache functionality"""
    print("🧪 Running Unit Tests for Cache...")
    print("=" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/test_cache.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Unit tests PASSED!")
            return True
        else:
            print("❌ Unit tests FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False

def run_integration_tests():
    """Run the integration tests for cache functionality"""
    print("\n🔄 Running Integration Tests for Cache...")
    print("=" * 45)
    
    try:
        result = subprocess.run([
            sys.executable, "test_cache_integration.py"
        ], cwd=os.getcwd())
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False

def main():
    """Run all cache tests"""
    print("🎯 COMPLETE CACHE TEST SUITE")
    print("=" * 50)
    
    results = []
    
    # Run unit tests
    results.append(run_unit_tests())
    
    # Run integration tests  
    results.append(run_integration_tests())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Test Suites Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL CACHE TESTS PASSED!")
        print("✅ Cache functionality is working perfectly")
    elif passed > 0:
        print("⚠️ SOME TESTS PASSED, some failed")
        print("🔧 Cache functionality needs some attention")
    else:
        print("❌ ALL TESTS FAILED")
        print("🚨 Cache functionality has serious issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
