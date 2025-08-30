#!/usr/bin/env python3
"""
Test Case Analysis Tool

This script analyzes the TestCases(1).xlsx file to:
1. Categorize queries by complexity and type
2. Identify potential challenges for the LLM
3. Provide recommendations for improvement
4. Generate insights for prompt engineering

Usage:
    uv run python tests/analysis/analyze_testcases.py
"""

import pandas as pd
import sys
import os
from pathlib import Path

def analyze_testcases():
    """Analyze test cases and categorize them"""
    try:
        # Find the Excel file (check both current directory and parent directories)
        excel_file = None
        for path in [Path("."), Path(".."), Path("../..")]:
            test_file = path / "TestCases (1).xlsx"
            if test_file.exists():
                excel_file = test_file
                break
        
        if not excel_file:
            raise FileNotFoundError("TestCases (1).xlsx not found")
            
        print(f"📂 Reading test cases from: {excel_file}")
        df = pd.read_excel(excel_file)
        
        print("📊 Test Cases Analysis")
        print("=" * 50)
        print(f"Total test cases: {len(df)}")
        print()
        
        # Display column names
        print("📋 Available columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        print()
        
        # Display first few rows to understand structure
        print("🔍 Sample test cases:")
        print(df.head(10).to_string())
        print()
        
        # Analyze question patterns if there's a question column
        question_cols = [col for col in df.columns if 'question' in col.lower() or 'query' in col.lower() or 'natural' in col.lower()]
        
        if question_cols:
            question_col = question_cols[0]
            print(f"📝 Analyzing questions from column: {question_col}")
            print()
            
            questions = df[question_col].dropna()
            
            # Categorize questions
            categories = {
                "Simple SELECT": [],
                "Aggregation (COUNT, SUM, AVG)": [],
                "JOINs": [],
                "Complex Conditions": [],
                "Date/Time Operations": [],
                "Subqueries": [],
                "Window Functions": [],
                "Other Complex": []
            }
            
            for idx, question in enumerate(questions):
                q = str(question).lower()
                
                if any(word in q for word in ["count", "sum", "avg", "max", "min", "group by"]):
                    categories["Aggregation (COUNT, SUM, AVG)"].append((idx+1, question))
                elif any(word in q for word in ["join", "inner", "left", "right", "outer"]):
                    categories["JOINs"].append((idx+1, question))
                elif any(word in q for word in ["date", "time", "yesterday", "last week", "month", "year"]):
                    categories["Date/Time Operations"].append((idx+1, question))
                elif any(word in q for word in ["subquery", "exists", "in (select", "not in"]):
                    categories["Subqueries"].append((idx+1, question))
                elif any(word in q for word in ["window", "over", "partition", "rank", "row_number"]):
                    categories["Window Functions"].append((idx+1, question))
                elif any(word in q for word in ["where", "and", "or", "between", "like", "having"]):
                    categories["Complex Conditions"].append((idx+1, question))
                elif len(q.split()) <= 10 and any(word in q for word in ["select", "show", "list", "get"]):
                    categories["Simple SELECT"].append((idx+1, question))
                else:
                    categories["Other Complex"].append((idx+1, question))
            
            # Print categorized results
            for category, items in categories.items():
                if items:
                    print(f"🎯 {category}: {len(items)} cases")
                    for idx, question in items[:3]:  # Show first 3 examples
                        print(f"   {idx}. {question}")
                    if len(items) > 3:
                        print(f"   ... and {len(items) - 3} more")
                    print()
        
        # Generate complexity analysis
        print("🔧 Complexity Analysis:")
        print("=" * 50)
        
        complexity_scores = {}
        for idx, question in enumerate(questions):
            q = str(question).lower()
            score = 0
            
            # Scoring factors
            if any(word in q for word in ["join", "inner", "left", "right", "outer"]): score += 2
            if any(word in q for word in ["count", "sum", "avg", "max", "min"]): score += 1
            if any(word in q for word in ["group by", "having"]): score += 2
            if any(word in q for word in ["subquery", "exists", "in (select"]): score += 3
            if any(word in q for word in ["window", "over", "partition"]): score += 4
            if any(word in q for word in ["date", "time", "interval"]): score += 2
            if q.count("and") + q.count("or") > 2: score += 1
            
            complexity_scores[idx+1] = score
        
        # Categorize by complexity
        simple = [k for k, v in complexity_scores.items() if v <= 2]
        medium = [k for k, v in complexity_scores.items() if 3 <= v <= 5]
        complex_queries = [k for k, v in complexity_scores.items() if v > 5]
        
        print(f"🟢 Simple (score ≤2): {len(simple)} queries")
        print(f"🟡 Medium (score 3-5): {len(medium)} queries") 
        print(f"🔴 Complex (score >5): {len(complex_queries)} queries")
        print()
        
        # Show most complex queries
        if complex_queries:
            print("🚨 Most Complex Queries (likely to fail):")
            sorted_complex = sorted([(k, complexity_scores[k]) for k in complex_queries], 
                                  key=lambda x: x[1], reverse=True)
            for test_id, score in sorted_complex[:5]:
                question = questions.iloc[test_id-1]
                print(f"   {test_id}. (Score: {score}) {question[:80]}...")
            print()
        
        return df, categories, complexity_scores
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        print("Make sure the file 'TestCases (1).xlsx' exists and is accessible")
        return None, None, None

def generate_recommendations(categories, complexity_scores):
    """Generate specific recommendations based on analysis"""
    print("💡 LLM Improvement Recommendations:")
    print("=" * 50)
    
    # Schema-specific recommendations
    print("1. 🗄️ Schema Context Enhancement:")
    print("   - Add exact column names for each table")
    print("   - Include data types and relationships")
    print("   - Provide sample data for context")
    print()
    
    # Query-specific recommendations
    if categories.get("JOINs"):
        print("2. 🔗 JOIN Operations:")
        print(f"   - {len(categories['JOINs'])} queries require JOINs")
        print("   - Add explicit JOIN examples to prompt")
        print("   - Include foreign key relationships")
        print()
    
    if categories.get("Aggregation (COUNT, SUM, AVG)"): 
        print("3. 📊 Aggregation Functions:")
        print(f"   - {len(categories['Aggregation (COUNT, SUM, AVG)'])} aggregation queries")
        print("   - Add GROUP BY examples")
        print("   - Include HAVING clause patterns")
        print()
    
    if categories.get("Date/Time Operations"):
        print("4. 📅 Date/Time Functions:")
        print(f"   - {len(categories['Date/Time Operations'])} date/time queries")
        print("   - Use SQLite date functions (strftime, date)")
        print("   - Avoid PostgreSQL-specific syntax")
        print()
    
    # Complexity-based recommendations
    complex_count = len([s for s in complexity_scores.values() if s > 5])
    if complex_count > 0:
        print("5. 🎯 Complex Query Optimization:")
        print(f"   - {complex_count} complex queries detected")
        print("   - Consider query simplification")
        print("   - Add timeout handling")
        print("   - Implement query cost analysis")
        print()
    
    print("6. 🛠️ Technical Improvements:")
    print("   - Implement SQLite syntax post-processing")
    print("   - Add query validation before execution")
    print("   - Create fallback patterns for common failures")
    print("   - Add query performance monitoring")
    print()

if __name__ == "__main__":
    print("🔍 TEST CASE ANALYSIS TOOL")
    print("=" * 60)
    print("Analyzing TestCases(1).xlsx to understand query patterns...")
    print()
    
    df, categories, complexity_scores = analyze_testcases()
    
    if df is not None:
        generate_recommendations(categories, complexity_scores)
        
        print("🎯 Next Steps:")
        print("1. Run this analysis before testing to understand challenges")
        print("2. Use insights to improve LLM prompts and post-processing")
        print("3. Focus on high-complexity queries for targeted improvements")
        print("4. Compare results with actual test outcomes")
        print()
        print("📊 Run comprehensive tests with:")
        print("   uv run python tests/comprehensive/test_all_cases.py")
