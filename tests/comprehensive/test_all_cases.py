#!/usr/bin/env python3
"""
Test script to run all test cases from Excel file and evaluate LLM performance
"""

import pandas as pd
import requests
import time
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_all_cases():
    """Test all cases from Excel file"""
    
    try:
        # Read test cases
        df = pd.read_excel("TestCases (1).xlsx")
        print(f"📊 Testing {len(df)} test cases...")
        print("=" * 60)
        
        results = []
        successful = 0
        failed = 0

        
        for idx, row in df.iterrows():
            test_id = row['Test Case ID']
            question = row['Natural Language Query']
            
            print(f"\n🧪 Test Case {test_id}: {question[:60]}...")
            
            try:
                # Make API request
                response = requests.post(f"{API_URL}/ask", json={
                    "question": question,
                    "role": "analyst",
                    "user": "test_user"
                }, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    table = data.get("table", {})
                    sql = data.get("explanation", "")
                    
                    # All queries now use LLM only
                    
                    if table.get("error"):
                        print(f"   ❌ FAILED: {table['error']}")
                        failed += 1
                        results.append({
                            "test_id": test_id,
                            "question": question,
                            "status": "FAILED",
                            "error": table['error'],
                            "sql": sql,
                            "method": "LLM"
                        })
                    else:
                        rows = table.get("rows", [])
                        row_count = len(rows) if isinstance(rows, list) else 0
                        print(f"   ✅ SUCCESS: {row_count} rows returned")
                        successful += 1
                        
                        # All queries use LLM
                        
                        results.append({
                            "test_id": test_id,
                            "question": question,
                            "status": "SUCCESS",
                            "rows": row_count,
                            "sql": sql,
                            "method": "LLM"
                        })
                else:
                    print(f"   ❌ API ERROR: {response.status_code}")
                    failed += 1
                    results.append({
                        "test_id": test_id,
                        "question": question,
                        "status": "API_ERROR",
                        "error": f"HTTP {response.status_code}",
                        "sql": "",
                        "method": "UNKNOWN"
                    })
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                failed += 1
                results.append({
                    "test_id": test_id,
                    "question": question,
                    "status": "EXCEPTION",
                    "error": str(e),
                    "sql": "",
                    "method": "UNKNOWN"
                })
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(df)}")
        print(f"✅ Successful: {successful} ({successful/len(df)*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/len(df)*100:.1f}%)")
        print(f"🤖 All queries processed by LLM")
        
        # Save detailed results
        results_df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_results_{timestamp}.csv"
        results_df.to_csv(results_file, index=False)
        print(f"\n📝 Detailed results saved to: {results_file}")
        
        # Show failed cases
        failed_cases = [r for r in results if r['status'] in ['FAILED', 'API_ERROR', 'EXCEPTION']]
        if failed_cases:
            print(f"\n❌ FAILED CASES ({len(failed_cases)}):")
            for case in failed_cases[:5]:  # Show first 5
                print(f"   {case['test_id']}: {case['question'][:50]}...")
                print(f"      Error: {case.get('error', 'Unknown error')}")
            if len(failed_cases) > 5:
                print(f"   ... and {len(failed_cases) - 5} more (see CSV for details)")
        
        # Show LLM success rate
        llm_cases = [r for r in results if r['method'] == 'LLM']
        if llm_cases:
            llm_success = len([r for r in llm_cases if r['status'] == 'SUCCESS'])
            print(f"\n🤖 LLM Performance: {llm_success}/{len(llm_cases)} ({llm_success/len(llm_cases)*100:.1f}% success rate)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error reading test cases: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Starting comprehensive test of all test cases...")
    print("Make sure the API is running at http://localhost:8000")
    print()
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API is not responding correctly")
            exit(1)
    except:
        print("❌ API is not running. Please start it with: uv run python run_app.py")
        exit(1)
    
    results = test_all_cases()
    
    if results:
        print("\n🎯 RECOMMENDATIONS FOR LLM IMPROVEMENT:")
        print("1. Review failed cases and add specific patterns to prompt")
        print("2. Enhance schema context with more examples")
        print("3. Add more post-processing rules for common errors")
        print("4. Consider fine-tuning on banking-specific queries")
        print("5. Implement query complexity analysis and routing")
