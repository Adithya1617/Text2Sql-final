import streamlit as st
import requests
import pandas as pd
import sqlite3, pathlib

st.set_page_config(page_title="Local NL → SQL (Offline)", layout="wide")
st.title("🧠 Local NL → SQL (Offline)")

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

user = st.text_input("User", value="test_user")
role = st.selectbox("Role", options=["analyst", "viewer", "admin"], index=0)
question = st.text_input("Ask a question", value="Top 5 branches by deposit amount")

if st.button("Ask"):
    with st.spinner("Running pipeline..."):
        try:
            r = requests.post(f"{API_URL}/ask", json={"question": question, "role": role, "user": user})
            if r.status_code == 200:
                data = r.json()

                # Create columns for better layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # SQL Generation Method Indicator
                    st.subheader("🤖 LLM-Generated SQL")
                    st.info("🧠 Using AI model for dynamic SQL generation")
                    st.info("💡 All queries are processed by the language model")
                    
                    # Show the SQL
                    st.subheader("📝 Generated SQL")
                    sql = data.get("sql", "")
                    st.code(sql, language="sql")
                    
                    # Show debugging info for LLM-generated SQL
                    if sql:
                        with st.expander("🔍 SQL Debug Info"):
                            st.text(f"SQL Length: {len(sql)} characters")
                            st.text(f"Contains SELECT: {'SELECT' in sql.upper()}")
                            st.text(f"Contains FROM: {'FROM' in sql.upper()}")
                            if ";" in sql:
                                st.warning("⚠️ Multiple statements detected - only first statement used")
                            
                            # Show SQL structure analysis
                            st.subheader("📊 SQL Structure Analysis")
                            if "count(" in sql_lower:
                                st.info("🔢 Contains COUNT operations")
                            if "group by" in sql_lower:
                                st.info("📊 Contains GROUP BY clause")
                            if "having" in sql_lower:
                                st.info("🎯 Contains HAVING clause")
                            if "order by" in sql_lower:
                                st.info("📈 Contains ORDER BY clause")
                            if "limit" in sql_lower:
                                st.info("🚫 Contains LIMIT clause")
                
                with col2:
                    # Guard and Security Info
                    st.subheader("🛡️ Security & Validation")
                    guard_reason = data.get('guard_reason', '')
                    if guard_reason:
                        st.success(f"✅ Guard: {guard_reason}")
                    
                    # Performance metrics
                    table = data.get("table", {})
                    if table.get("elapsed_sec"):
                        st.metric("⏱️ Query Time", f"{table['elapsed_sec']:.3f}s")
                    
                    # Row count
                    rows = table.get("rows", [])
                    if isinstance(rows, list):
                        st.metric("📊 Results", len(rows))
                
                # Show results
                st.subheader("📊 Query Results")
                table = data.get("table", {})
                if table.get("error"):
                    st.error(f"❌ Query Error: {table['error']}")
                    
                    # Provide helpful error analysis
                    with st.expander("🔍 Error Analysis"):
                        error_msg = table['error'].lower()
                        if "syntax error" in error_msg:
                            st.warning("🔧 **SQL Syntax Issue Detected**")
                            st.info("The generated SQL has syntax problems. This usually means:")
                            st.info("• The LLM generated invalid SQL")
                            st.info("• The LLM may need more specific context or examples")
                            st.info("• The query might be too complex for the current model")
                        elif "security" in error_msg or "guard" in error_msg:
                            st.warning("🛡️ **Security Validation Failed**")
                            st.info("The query was blocked for security reasons:")
                            st.info("• Only SELECT statements are allowed")
                            st.info("• Multiple statements are not permitted")
                            st.info("• Access to system tables is restricted")
                        else:
                            st.info("💡 **General Query Error**")
                            st.info("The query failed during execution. Check the error details above.")
                else:
                    rows = table.get("rows", [])
                    if isinstance(rows, list) and rows:
                        df = pd.DataFrame(rows)
                        st.dataframe(df, use_container_width=True)
                        
                        # Show summary statistics if numeric data
                        if len(df.columns) > 1 and df.iloc[:, 1].dtype in ['int64', 'float64']:
                            st.subheader("📈 Summary Statistics")
                            st.write(f"**Total Results:** {len(df)}")
                            if len(df.columns) > 1:
                                numeric_col = df.iloc[:, 1]
                                if numeric_col.dtype in ['int64', 'float64']:
                                    st.write(f"**Sum:** {numeric_col.sum():.2f}")
                                    st.write(f"**Average:** {numeric_col.mean():.2f}")
                                    st.write(f"**Min:** {numeric_col.min():.2f}")
                                    st.write(f"**Max:** {numeric_col.max():.2f}")
                    elif isinstance(rows, dict):
                        st.json(rows)
                    else:
                        st.info("ℹ️ No rows returned.")
                        
                        # Provide helpful feedback for no results
                        with st.expander("💡 No Results - Possible Reasons"):
                            st.info("• The query might be too specific")
                            st.info("• There might be no data matching the criteria")
                            st.info("• The SQL might need adjustment")
                            st.info("• Try rephrasing the question with more specific terms")
                        
            elif r.status_code == 403:
                st.error("❌ You do not have permission to run this query.")
            else:
                st.error(f"API error: {r.status_code} - {r.text}")
        except Exception as e:
            st.error(f"Failed to call API: {e}")

# Sidebar with recent queries
def get_history(limit=10):
    DB_PATH = pathlib.Path("app/data.db")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT user, role, question, safe_sql, ts FROM logs ORDER BY ts DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return rows
    except:
        return []

with st.sidebar:
    st.subheader("🕑 Recent Queries")
    history = get_history()
    if history:
        for u, r, q, sql, ts in history:
            with st.expander(f"[{ts}] {u} ({r})"):
                st.text(f"Question: {q}")
                if sql:
                    st.code(sql, language="sql")
    else:
        st.info("No query history yet")
    
    st.subheader("ℹ️ About")
    st.markdown("""
    **Local Orchestrator** uses:
    - 🤖 **LLM**: AI-powered SQL generation
    - 🤖 **LLM-Powered**: AI-driven SQL generation
    - 🛡️ **Guards**: Security validation
    - 📊 **Execution**: SQLite database
    """)
