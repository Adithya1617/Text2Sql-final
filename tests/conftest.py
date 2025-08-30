import pytest
import pathlib
import sqlite3
from fastapi.testclient import TestClient
from app.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary test database"""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create test schema
    cur.executescript("""
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE branches (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL
    );
    
    CREATE TABLE customers (
        id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        branch_id TEXT,
        FOREIGN KEY (branch_id) REFERENCES branches(id)
    );
    
    CREATE TABLE employees (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        branch_id TEXT,
        FOREIGN KEY (branch_id) REFERENCES branches(id)
    );

    CREATE TABLE accounts (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        branch_id TEXT
        type TEXT NOT NULL,
        balance REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (branch_id) REFERENCES branches(id)
    );
    
    CREATE TABLE transactions (
        id TEXT PRIMARY KEY,
        account_id TEXT,
        employee_id TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        transaction_date TEXT, -- Added
        description TEXT, -- Added
        FOREIGN KEY (account_id) REFERENCES accounts(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );

    CREATE TABLE loans (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        loan_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    
    -- Create view for viewer role (limited customer data)
    CREATE VIEW viewer_customers AS
    SELECT id, first_name, last_name, branch_id
    FROM customers;
    """)
    
    # Insert test data
    cur.executemany("INSERT INTO branches VALUES (?, ?, ?, ?)", [
        ("BR001", "Downtown", "New York", "NY"),
        ("BR002", "Uptown", "Chicago", "IL"),
        ("BR003", "Midtown", "New York", "NY")
    ])
    
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", [
        ("CUST001", "John", "Doe", "BR001"),
        ("CUST002", "Jane", "Smith", "BR002"),
        ("CUST003", "Peter", "Jones", "BR001"),
        ("CUST004", "Mary", "Johnson", "BR003"),
    ])

    cur.executemany("INSERT INTO employees VALUES (?, ?, ?)", [
        ("EMP001", "Alice", "BR001"),
        ("EMP002", "Bob", "BR002"),
        ("EMP003", "Charlie", "BR001"),
    ])
    
    cur.executemany("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)", [
        ("ACC001", "CUST001", "BR001", "savings", 1000.0),
        ("ACC002", "CUST002", "BR002", "checking", 2500.0),
        ("ACC003", "CUST003", "BR001", "savings", 5000.0),
        ("ACC004", "CUST004", "BR003", "checking", 100.0)
    ])
    
    cur.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)", [
        ("TXN001", "ACC001", "EMP001", 500.0, "deposit", "2023-01-15T10:00:00Z", "Initial deposit"),
        ("TXN002", "ACC002", "EMP002", 1000.0, "deposit", "2023-01-16T11:00:00Z", "Paycheck"),
        ("TXN003", "ACC003", "EMP003", 2000.0, "deposit", "2023-01-18T13:00:00Z", "Transfer"),
        ("TXN004", "ACC002", "EMP002", 1500.0, "deposit", "2023-01-19T14:00:00Z", "Paycheck"),
        ("TXN005", "ACC004", "EMP003", 50.0, "deposit", "2023-01-20T15:00:00Z", "Cash deposit"),
        ("TXN006", "ACC001", "EMP001", -200.0, "withdrawal", "2023-01-21T16:00:00Z", "Bill payment")
    ])
    
    cur.executemany("INSERT INTO loans VALUES (?, ?, ?, ?)", [
        ("LOAN001", "CUST001", 10000.0, "approved"),
        ("LOAN002", "CUST003", 5000.0, "pending")
    ])
    
    conn.commit()
    conn.close()
    
    return db_path

@pytest.fixture
def test_db(test_db_path, monkeypatch):
    """Patch the application to use the test database"""
    monkeypatch.setattr("app.models.sql_agent.DB_PATH", test_db_path)
    monkeypatch.setattr("app.executors.sqlite_exec.DB_PATH", test_db_path)
    return test_db_path
