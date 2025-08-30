#!/usr/bin/env python3
"""
Master Test Runner for Local SQL Query Orchestrator

This script provides a unified interface to run different categories of tests.
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_prerequisites():
    """Check if required services are running"""
    print("🔍 Checking Prerequisites...")
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama server running with {len(models)} models")
            
            # Check for required model
            model_names = [m.get("name", "") for m in models]
            if "hf.co/defog/sqlcoder-7b-2:latest" in model_names:
                print("✅ Required LLM model available")
            else:
                print("⚠️ Required model not found. Run: ollama pull hf.co/defog/sqlcoder-7b-2:latest")
        else:
            print("⚠️ Ollama server not responding correctly")
            return False
    except Exception:
        print("⚠️ Ollama server not reachable. Start with: ollama serve")
        return False
    
    # Check if backend is running (for integration tests)
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend API is running")
        else:
            print("⚠️ Backend API not responding. Start with: uv run python run_app.py")
    except Exception:
        print("ℹ️ Backend API not running (required for integration tests)")
    
    return True

def run_unit_tests():
    """Run all unit tests"""
    return run_command(
        "uv run pytest tests/unit/ -v --tb=short",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "uv run pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    )

def run_comprehensive_tests():
    """Run comprehensive end-to-end tests"""
    results = []
    
    # Test all cases
    results.append(run_command(
        "uv run python tests/comprehensive/test_all_cases.py",
        "All Test Cases (35 questions)"
    ))
    
    # LLM integration test
    results.append(run_command(
        "uv run python tests/comprehensive/test_llm_integration.py",
        "LLM Integration Test"
    ))
    
    # Cache integration test
    results.append(run_command(
        "uv run python tests/comprehensive/test_cache_integration.py",
        "Cache Integration Test"
    ))
    
    return all(results)

def run_analysis_tools():
    """Run analysis tools"""
    return run_command(
        "uv run python tests/analysis/analyze_testcases.py",
        "Test Case Analysis"
    )

def run_manual_tests():
    """Run manual tests"""
    results = []
    
    results.append(run_command(
        "uv run python tests/manual/quick_cache_test.py",
        "Quick Cache Test"
    ))
    
    results.append(run_command(
        "uv run python tests/manual/debug_imports.py",
        "Import Debug Test"
    ))
    
    return all(results)

def run_all_tests():
    """Run all test categories"""
    print("🚀 Running Complete Test Suite")
    print("=" * 60)
    
    results = {
        "Prerequisites": check_prerequisites(),
        "Analysis Tools": run_analysis_tools(),
        "Unit Tests": run_unit_tests(),
        "Integration Tests": run_integration_tests(),
        "Comprehensive Tests": run_comprehensive_tests(),
        "Manual Tests": run_manual_tests()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST EXECUTION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for category, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {category}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} categories passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️ Some tests failed. Check logs above for details.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run tests for Local SQL Query Orchestrator")
    parser.add_argument(
        "category",
        nargs="?",
        choices=["analysis", "unit", "integration", "comprehensive", "manual", "all"],
        default="all",
        help="Test category to run (default: all)"
    )
    parser.add_argument(
        "--no-prereq-check",
        action="store_true",
        help="Skip prerequisite checks"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    print("🧪 LOCAL SQL QUERY ORCHESTRATOR - TEST RUNNER")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Running: {args.category} tests")
    
    if not args.no_prereq_check:
        if not check_prerequisites():
            print("\n⚠️ Prerequisites not met. Use --no-prereq-check to skip.")
            return False
    
    # Add coverage flag if requested
    if args.coverage and args.category in ["unit", "integration", "all"]:
        os.environ["PYTEST_ADDOPTS"] = "--cov=app --cov-report=html --cov-report=term"
    
    # Run selected test category
    if args.category == "analysis":
        success = run_analysis_tools()
    elif args.category == "unit":
        success = run_unit_tests()
    elif args.category == "integration":
        success = run_integration_tests()
    elif args.category == "comprehensive":
        success = run_comprehensive_tests()
    elif args.category == "manual":
        success = run_manual_tests()
    else:  # all
        success = run_all_tests()
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.coverage and success:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
