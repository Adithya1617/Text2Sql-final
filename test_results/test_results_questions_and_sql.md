# Test Results: Questions and Generated SQL Queries

**Test Date:** August 31, 2025  
**Total Questions:** 35  
**Success Rate:** 19/35 (54.3%)  
**LLM Model:** hf.co/defog/sqlcoder-7b-2:latest

---

## Test Case 1
**Question:** List all branches and their managers' names. Include branches without a manager.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT b.name, COALESCE(e.first_name, e.last_name) AS manager_name 
FROM branches b 
LEFT JOIN employees e ON b.manager_id = e.id 
GROUP BY b.name, e.first_name, e.last_name 
ORDER BY b.name NULLS LAST
```
**Error:** SQL Execution Error: no such column: e.first_name

---

## Test Case 2
**Question:** Find the names of customers who have both 'checking' and 'savings' accounts.  
**Status:** ✅ SUCCESS (179 rows)  
**Generated SQL:**
```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
WHERE a.type IN ('checking', 'savings') 
GROUP BY c.id, c.first_name, c.last_name 
HAVING COUNT(DISTINCT a.type) = 2
```

---

## Test Case 3
**Question:** List all employees who have handled a transaction for a customer born before 1960.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT e.first_name, e.last_name 
FROM employees e 
JOIN transactions t ON e.id = t.employee_id 
JOIN accounts a ON a.id = t.account_id 
JOIN customers c ON c.id = a.customer_id 
WHERE date_part('year', c.date_of_birth) < 1960
```
**Error:** SQL Execution Error: no such column: e.first_name

---

## Test Case 4
**Question:** Find the total number of accounts for each customer gender.  
**Status:** ✅ SUCCESS (4 rows)  
**Generated SQL:**
```sql
SELECT c.gender, COUNT(a.id) AS total_accounts 
FROM customers c 
JOIN accounts a ON a.customer_id = c.id 
GROUP BY c.gender 
ORDER BY total_accounts DESC
```

---

## Test Case 5
**Question:** For each employee position, what is the average salary, but only include positions with more than 2 employees?  
**Status:** ✅ SUCCESS (12 rows)  
**Generated SQL:**
```sql
SELECT position, AVG(salary) AS average_salary 
FROM employees 
GROUP BY position 
HAVING COUNT(*) > 2 
ORDER BY average_salary DESC
```

---

## Test Case 6
**Question:** Show the average transaction amount for transactions completed on weekdays only.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT AVG(amount) AS average_amount 
FROM transactions 
WHERE strftime('%w', transaction_date) NOT IN ('0', '6')
```
**Error:** SQL Syntax Error: near "FROM": syntax error. Please check the generated SQL.

---

## Test Case 7
**Question:** Which employees were hired in the same month as 'Raymond Jefferson'?  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT * FROM employees 
WHERE strftime('%Y-%m', hire_date) = (
    SELECT strftime('%Y-%m', hire_date) 
    FROM employees 
    WHERE name ilike '%Raymond Jefferson%'
)
```
**Error:** SQL Syntax Error: near "ilike": syntax error. Please check the generated SQL.

---

## Test Case 8
**Question:** For each customer, list their total deposit amount and total withdrawal amount.  
**Status:** ❌ TIMEOUT  
**Generated SQL:**
```sql
SELECT c.first_name, c.last_name,
       SUM(CASE WHEN t.type = 'deposit' THEN t.amount ELSE 0 END) AS total_deposits,
       SUM(CASE WHEN t.type = 'withdrawal' THEN t.amount ELSE 0 END) AS total_withdrawals
FROM customers c
JOIN accounts a ON c.id = a.customer_id
JOIN transactions t ON a.id = t.account_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY c.last_name, c.first_name
```
**Error:** HTTPConnectionPool timeout (30s)

---

## Test Case 9
**Question:** Identify employees who have handled transactions for customers from more than 3 different branches.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT e.first_name, e.last_name 
FROM employees e 
JOIN transactions t ON e.id = t.employee_id 
JOIN accounts a ON t.account_id = a.id 
JOIN customers c ON a.customer_id = c.id 
GROUP BY e.id, e.first_name, e.last_name 
HAVING COUNT(DISTINCT c.branch_id) > 3
```
**Error:** SQL Execution Error: no such column: e.first_name

---

## Test Case 10
**Question:** Find the names of branches where the average salary of employees is above the overall average salary.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT b.name 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
GROUP BY b.id, b.name 
HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)
```
**Error:** SQL Execution Error: misuse of aggregate function AVG()

---

## Test Case 11
**Question:** List customers who have a 'credit' account and have made at least one transaction in the last 30 days.  
**Status:** ✅ SUCCESS (200 rows)  
**Generated SQL:**
```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
JOIN transactions t ON a.id = t.account_id 
WHERE a.type = 'credit' 
AND t.transaction_date >= date('now', '-30 days') 
ORDER BY c.last_name, c.first_name LIMIT 200
```

---

## Test Case 12
**Question:** Show customers who have the same first name but different last names.  
**Status:** ✅ SUCCESS (200 rows)  
**Generated SQL:**
```sql
SELECT c1.first_name, c1.last_name, c2.last_name AS other_last_name 
FROM customers c1 
JOIN customers c2 ON c1.first_name = c2.first_name AND c1.last_name != c2.last_name 
WHERE c1.id < c2.id 
ORDER BY c1.first_name, c1.last_name LIMIT 200
```

---

## Test Case 13
**Question:** List the branches where the total salary of employees is less than $50,000.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT b.name 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
GROUP BY b.id, b.name 
HAVING SUM(e.salary) < 50000
```
**Error:** SQL Execution Error: misuse of aggregate function SUM()

---

## Test Case 14
**Question:** Show the email and phone number of customers who have a 'loan' account.  
**Status:** ✅ SUCCESS (3 rows)  
**Generated SQL:**
```sql
SELECT DISTINCT c.email, c.phone 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
WHERE a.type = 'loan'
```

---

## Test Case 15
**Question:** For each employee position, list the number of employees and the total salary cost.  
**Status:** ✅ SUCCESS (12 rows)  
**Generated SQL:**
```sql
SELECT position, COUNT(*) AS employee_count, SUM(salary) AS total_salary_cost 
FROM employees 
GROUP BY position 
ORDER BY total_salary_cost DESC
```

---

## Test Case 16
**Question:** List all transactions that occurred on a weekend (Saturday or Sunday).  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT * FROM transactions 
WHERE strftime('%w', transaction_date) IN ('0', '6') 
ORDER BY transaction_date DESC LIMIT 200
```
**Error:** SQL Syntax Error: near "FROM": syntax error. Please check the generated SQL.

---

## Test Case 17
**Question:** Find the customers who have made transactions on consecutive days.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
JOIN transactions t1 ON a.id = t1.account_id 
JOIN transactions t2 ON a.id = t2.account_id 
WHERE date(t2.transaction_date) = date(t1.transaction_date, '+1 day')
```
**Error:** SQL Syntax Error: near "'1 day'": syntax error. Please check the generated SQL.

---

## Test Case 18
**Question:** List all accounts that have more deposits than withdrawals in terms of count.  
**Status:** ❌ TIMEOUT  
**Generated SQL:**
```sql
SELECT a.id, a.type, a.balance,
       COUNT(CASE WHEN t.type = 'deposit' THEN 1 END) AS deposit_count,
       COUNT(CASE WHEN t.type = 'withdrawal' THEN 1 END) AS withdrawal_count
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id
GROUP BY a.id, a.type, a.balance
HAVING COUNT(CASE WHEN t.type = 'deposit' THEN 1 END) > COUNT(CASE WHEN t.type = 'withdrawal' THEN 1 END)
ORDER BY deposit_count DESC
```
**Error:** HTTPConnectionPool timeout (30s)

---

## Test Case 19
**Question:** For each customer, list their first name, last name, and the total number of transactions they have made.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT c.first_name, c.last_name, COUNT(t.id) AS total_transactions 
FROM customers c 
LEFT JOIN accounts a ON c.id = a.customer_id 
LEFT JOIN transactions t ON a.id = t.account_id 
GROUP BY c.id, c.first_name, c.last_name 
ORDER BY total_transactions DESC LIMIT 200
```
**Error:** SQL Syntax Error: near "FROM": syntax error. Please check the generated SQL.

---

## Test Case 20
**Question:** Find the average balance of accounts that have had at least one transaction.  
**Status:** ✅ SUCCESS (1 row)  
**Generated SQL:**
```sql
SELECT AVG(a.balance) AS average_balance 
FROM accounts a 
WHERE EXISTS (
    SELECT 1 FROM transactions t WHERE t.account_id = a.id
)
```

---

## Test Case 21
**Question:** Get the names of customers who have the same last name as their assigned employee (if any).  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
JOIN transactions t ON a.id = t.account_id 
JOIN employees e ON t.employee_id = e.id 
WHERE c.last_name = e.last_name
```
**Error:** SQL Execution Error: no such column: e.first_name

---

## Test Case 22
**Question:** List all accounts that have never had a 'withdrawal' transaction.  
**Status:** ✅ SUCCESS (200 rows)  
**Generated SQL:**
```sql
SELECT a.id, a.type, a.balance 
FROM accounts a 
WHERE NOT EXISTS (
    SELECT 1 FROM transactions t 
    WHERE t.account_id = a.id AND t.type = 'withdrawal'
) 
ORDER BY a.id LIMIT 200
```

---

## Test Case 23
**Question:** Show the average salary of employees for each branch, only considering branches with more than 1 employee.  
**Status:** ✅ SUCCESS (50 rows)  
**Generated SQL:**
```sql
SELECT b.name, AVG(e.salary) AS average_salary 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
GROUP BY b.id, b.name 
HAVING COUNT(e.id) > 1 
ORDER BY average_salary DESC LIMIT 200
```

---

## Test Case 24
**Question:** List customers who have a total transaction amount (sum of all transactions) greater than $10,000.  
**Status:** ✅ SUCCESS (2 rows)  
**Generated SQL:**
```sql
SELECT c.first_name, c.last_name, SUM(ABS(t.amount)) AS total_transaction_amount 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
JOIN transactions t ON a.id = t.account_id 
GROUP BY c.id, c.first_name, c.last_name 
HAVING SUM(ABS(t.amount)) > 10000 
ORDER BY total_transaction_amount DESC
```

---

## Test Case 25
**Question:** Find the branch with the most diverse set of employee positions (highest number of unique positions).  
**Status:** ✅ SUCCESS (1 row)  
**Generated SQL:**
```sql
SELECT b.name, COUNT(DISTINCT e.position) AS position_count 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
GROUP BY b.id, b.name 
ORDER BY position_count DESC 
LIMIT 1
```

---

## Test Case 26
**Question:** Find the total number of customers for each gender, excluding customers with 'prefer_not_to_say'.  
**Status:** ✅ SUCCESS (3 rows)  
**Generated SQL:**
```sql
SELECT gender, COUNT(*) AS total_customers 
FROM customers 
WHERE gender != 'prefer_not_to_say' 
GROUP BY gender 
ORDER BY total_customers DESC
```

---

## Test Case 27
**Question:** List all customers who have exactly two accounts.  
**Status:** ✅ SUCCESS (200 rows)  
**Generated SQL:**
```sql
SELECT c.first_name, c.last_name 
FROM customers c 
JOIN accounts a ON c.id = a.customer_id 
GROUP BY c.id, c.first_name, c.last_name 
HAVING COUNT(a.id) = 2 
ORDER BY c.last_name, c.first_name LIMIT 200
```

---

## Test Case 28
**Question:** Get the names of branches that have no managers assigned yet.  
**Status:** ✅ SUCCESS (50 rows)  
**Generated SQL:**
```sql
SELECT name 
FROM branches 
WHERE manager_id IS NULL 
ORDER BY name LIMIT 200
```

---

## Test Case 29
**Question:** Show the names of branches that have an employee named 'Michael'.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT DISTINCT b.name 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
WHERE e.name ILIKE '%Michael%'
```
**Error:** SQL Syntax Error: near "ILIKE": syntax error. Please check the generated SQL.

---

## Test Case 30
**Question:** List customers who share the same address with another customer.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT vc1.first_name, vc1.last_name, vc1.address 
FROM viewer_customers vc1 
JOIN viewer_customers vc2 ON vc1.address = vc2.address 
AND vc1.id != vc2.id 
ORDER BY vc1.address, vc1.last_name
```
**Error:** SQL Execution Error: no such column: vc1.address

---

## Test Case 31
**Question:** Find the branch that has the highest number of 'completed' transactions.  
**Status:** ✅ SUCCESS (1 row)  
**Generated SQL:**
```sql
SELECT b.name, COUNT(t.id) AS completed_transactions 
FROM branches b 
JOIN employees e ON b.id = e.branch_id 
JOIN transactions t ON e.id = t.employee_id 
WHERE t.status = 'completed' 
GROUP BY b.id, b.name 
ORDER BY completed_transactions DESC 
LIMIT 1
```

---

## Test Case 32
**Question:** Show the names of employees who have never handled a 'failed' transaction.  
**Status:** ✅ SUCCESS (200 rows)  
**Generated SQL:**
```sql
SELECT DISTINCT e.name 
FROM employees e 
WHERE e.id NOT IN (
    SELECT DISTINCT t.employee_id 
    FROM transactions t 
    WHERE t.status = 'failed' AND t.employee_id IS NOT NULL
) 
ORDER BY e.name LIMIT 200
```

---

## Test Case 33
**Question:** List customers who have a credit account and a loan account, but no savings account.  
**Status:** ✅ SUCCESS (2 rows)  
**Generated SQL:**
```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
WHERE EXISTS (SELECT 1 FROM accounts a WHERE a.customer_id = c.id AND a.type = 'credit') 
AND EXISTS (SELECT 1 FROM accounts a WHERE a.customer_id = c.id AND a.type = 'loan') 
AND NOT EXISTS (SELECT 1 FROM accounts a WHERE a.customer_id = c.id AND a.type = 'savings')
```

---

## Test Case 34
**Question:** Find the average balance of accounts for customers whose age is between 25 and 35.  
**Status:** ❌ FAILED  
**Generated SQL:**
```sql
SELECT AVG(a.balance) AS average_balance 
FROM accounts a 
JOIN customers c ON a.customer_id = c.id 
WHERE (julianday('now') - julianday(c.date_of_birth)) / 365.25 BETWEEN 25 AND 35
```
**Error:** SQL Syntax Error: near "FROM": syntax error. Please check the generated SQL.

---

## Test Case 35
**Question:** Show the names of branches that have at least one employee for every position available in the company.  
**Status:** ✅ SUCCESS (0 rows)  
**Generated SQL:**
```sql
SELECT b.name 
FROM branches b 
WHERE (
    SELECT COUNT(DISTINCT e.position) 
    FROM employees e 
    WHERE e.branch_id = b.id
) = (
    SELECT COUNT(DISTINCT position) 
    FROM employees
) 
ORDER BY b.name
```

---

## Summary

- **Total Questions:** 35
- **Successful Queries:** 19 (54.3%)
- **Failed Queries:** 16 (45.7%)
- **Common Issues:**
  - Column name errors (e.g., `e.first_name` doesn't exist)
  - SQL syntax errors with SQLite-specific functions
  - Timeout issues on complex queries
  - Case sensitivity issues with `ILIKE` vs `LIKE`

**LLM Model Performance:** The `hf.co/defog/sqlcoder-7b-2:latest` model shows good understanding of SQL structure and business logic, but needs improvements in:
1. Understanding the actual database schema column names
2. SQLite-specific syntax compatibility
3. Query optimization for complex operations
