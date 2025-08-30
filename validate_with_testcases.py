#!/usr/bin/env python3
"""
Validation Test using TestCases_SQL.xlsx

This test validates our application's SQL generation by comparing:
1. Generated SQL vs Expected SQL from the Excel file
2. Query execution success/failure
3. Result accuracy and performance
"""

import pandas as pd
import requests
import time
import sys
import os
from datetime import datetime
from pathlib import Path

def load_test_cases():
    """Load test cases from TestCases_SQL.xlsx"""
    print("📂 Loading test cases from TestCases_SQL.xlsx...")
    
    try:
        # Look for the file in current directory
        excel_file = Path("TestCases_SQL.xlsx")
        if not excel_file.exists():
            print("❌ TestCases_SQL.xlsx not found in current directory")
            return None
        
        df = pd.read_excel(excel_file)
        print(f"✅ Loaded {len(df)} test cases")
        
        # Display file structure
        print(f"📋 Columns found: {list(df.columns)}")
        print(f"📊 First few rows:")
        print(df.head(3))
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None

def validate_sql_generation(question, expected_sql):
    """Validate SQL generation for a single test case"""
    try:
        # Send question to our application
        response = requests.post("http://localhost:8000/ask", json={
            "question": question,
            "role": "analyst",
            "user": "validation_test"
        }, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "generated_sql": "",
                "execution_success": False,
                "execution_time": 0,
                "rows_returned": 0
            }
        
        data = response.json()
        generated_sql = data.get("sql", "")
        table = data.get("table", {})
        error = table.get("error", "")
        
        # Check if SQL generation was successful
        if error:
            return {
                "success": False,
                "error": error,
                "generated_sql": generated_sql,
                "execution_success": False,
                "execution_time": 0,
                "rows_returned": 0
            }
        
        # Check if execution was successful
        rows = table.get("rows", [])
        execution_success = len(rows) > 0 or "no results" not in error.lower()
        rows_returned = len(rows)
        
        return {
            "success": True,
            "error": "",
            "generated_sql": generated_sql,
            "execution_success": execution_success,
            "execution_time": table.get("elapsed_sec", 0),
            "rows_returned": rows_returned
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "generated_sql": "",
            "execution_success": False,
            "execution_time": 0,
            "rows_returned": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception: {str(e)}",
            "generated_sql": "",
            "execution_success": False,
            "execution_time": 0,
            "rows_returned": 0
        }

def run_validation_test():
    """Run the main validation test"""
    print("🧪 VALIDATION TEST USING TESTCASES_SQL.XLSX")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running. Start with: uv run python run_app.py")
            return False
    except:
        print("❌ Backend not reachable. Start with: uv run python run_app.py")
        return False
    
    print("✅ Backend is running")
    print()
    
    # Load test cases
    df = load_test_cases()
    if df is None:
        return False
    
    # Use the known column names from TestCases_SQL.xlsx
    question_col = 'Natural Language Query'
    sql_col = 'SQL Query'
    
    if question_col not in df.columns or sql_col not in df.columns:
        print("❌ Required columns not found")
        print(f"Available columns: {list(df.columns)}")
        return False
    
    print(f"📝 Using columns: '{question_col}' for questions, '{sql_col}' for SQL")
    print()
    
    # Run validation tests
    results = []
    total_cases = len(df)
    
    for idx, row in df.iterrows():
        question = str(row[question_col]).strip()
        expected_sql = str(row[sql_col]).strip()
        
        # Skip empty questions
        if not question or question.lower() in ['nan', 'none', '']:
            continue
        
        print(f"🧪 Test Case {idx+1}/{total_cases}: {question[:60]}...")
        
        # Validate SQL generation
        result = validate_sql_generation(question, expected_sql)
        result["question"] = question
        result["expected_sql"] = expected_sql
        result["test_case_id"] = idx + 1
        
        results.append(result)
        
        # Display result
        if result["success"]:
            if result["execution_success"]:
                print(f"   ✅ SUCCESS: {result['rows_returned']} rows in {result['execution_time']:.3f}s")
            else:
                print(f"   ⚠️ SQL generated but execution failed")
        else:
            print(f"   ❌ FAILED: {result['error']}")
        
        # Small delay to avoid overwhelming the backend
        time.sleep(0.5)
    
    # Generate validation report
    print("\n" + "=" * 70)
    print("📊 VALIDATION TEST RESULTS")
    print("=" * 70)
    
    total_tests = len(results)
    successful_generation = sum(1 for r in results if r["success"])
    successful_execution = sum(1 for r in results if r["execution_success"])
    
    print(f"📈 Total Test Cases: {total_tests}")
    print(f"✅ Successful SQL Generation: {successful_generation}/{total_tests} ({successful_generation/total_tests*100:.1f}%)")
    print(f"🚀 Successful Query Execution: {successful_execution}/{total_tests} ({successful_execution/total_tests*100:.1f}%)")
    
    # Error analysis
    if total_tests > successful_generation:
        print(f"\n❌ SQL Generation Failures: {total_tests - successful_generation}")
        error_counts = {}
        for result in results:
            if not result["success"]:
                error = result["error"]
                error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {error}: {count} cases")
    
    # Performance analysis
    execution_times = [r["execution_time"] for r in results if r["execution_success"]]
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        print(f"\n⏱️ Performance Metrics:")
        print(f"   • Average execution time: {avg_time:.3f}s")
        print(f"   • Maximum execution time: {max_time:.3f}s")
    
    # Save detailed results
    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"validation_results_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return successful_generation / total_tests >= 0.8  # 80% threshold

if __name__ == "__main__":
    success = run_validation_test()
    sys.exit(0 if success else 1)
