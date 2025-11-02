# SQL Study Guide

A comprehensive guide to mastering SQL for database classes.

## Table of Contents

1. [Fundamentals](#fundamentals)
2. [SELECT Statements](#select-statements)
3. [Filtering & WHERE Clause](#filtering--where-clause)
4. [JOINs](#joins)
5. [Aggregation & Grouping](#aggregation--grouping)
6. [Subqueries](#subqueries)
7. [Data Modification](#data-modification)
8. [Advanced Topics](#advanced-topics)
9. [Practice Problems](#practice-problems)

---

## Fundamentals

### What is SQL?
SQL (Structured Query Language) is a standardized language for managing and manipulating relational databases.

### Key Concepts
- **Tables**: Organized collections of data with rows and columns
- **Rows**: Individual records in a table
- **Columns**: Attributes or fields that define what data is stored
- **Primary Key**: Unique identifier for each row
- **Foreign Key**: Reference to a primary key in another table
- **Schema**: Structure and relationships of database objects

### Data Types
| Type | Description | Examples |
|------|-------------|----------|
| `INT`, `BIGINT` | Integer numbers | 42, -100, 2147483647 |
| `FLOAT`, `DECIMAL` | Decimal numbers | 3.14, 99.99 |
| `VARCHAR(n)` | Variable-length text | 'hello', 'database' |
| `CHAR(n)` | Fixed-length text | 'A', 'B' |
| `DATE` | Date values | '2025-11-01' |
| `TIMESTAMP` | Date and time | '2025-11-01 14:30:00' |
| `BOOLEAN` | True/False | TRUE, FALSE |

---

## SELECT Statements

### Basic Syntax
```sql
SELECT column1, column2, ...
FROM table_name;
```

### Examples
```sql
-- Select all columns
SELECT * FROM customers;

-- Select specific columns
SELECT first_name, last_name, email FROM customers;

-- Select with aliases
SELECT 
  first_name AS 'First Name',
  last_name AS 'Last Name'
FROM customers;

-- Select distinct values
SELECT DISTINCT country FROM customers;

-- Select with calculation
SELECT 
  product_name,
  price,
  price * 1.1 AS 'Price with 10% increase'
FROM products;
```

---

## Filtering & WHERE Clause

### WHERE Syntax
```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

### Comparison Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal | `age = 25` |
| `!=` or `<>` | Not equal | `age != 25` |
| `>` | Greater than | `salary > 50000` |
| `<` | Less than | `salary < 50000` |
| `>=` | Greater or equal | `age >= 18` |
| `<=` | Less or equal | `age <= 65` |

### Logical Operators
```sql
-- AND: Both conditions must be true
SELECT * FROM employees 
WHERE salary > 50000 AND department = 'Sales';

-- OR: At least one condition must be true
SELECT * FROM employees 
WHERE department = 'Sales' OR department = 'Marketing';

-- NOT: Condition must be false
SELECT * FROM employees 
WHERE NOT department = 'Sales';
```

### Advanced Filtering
```sql
-- IN: Check if value is in a list
SELECT * FROM orders WHERE status IN ('pending', 'processing', 'shipped');

-- BETWEEN: Check if value is in a range
SELECT * FROM sales WHERE sale_date BETWEEN '2025-01-01' AND '2025-12-31';

-- LIKE: Pattern matching (% = any characters, _ = single character)
SELECT * FROM customers WHERE email LIKE '%@gmail.com';
SELECT * FROM products WHERE product_name LIKE 'iPhone_%';

-- NULL checks
SELECT * FROM users WHERE phone_number IS NULL;
SELECT * FROM users WHERE phone_number IS NOT NULL;
```

---

## JOINs

JOINs combine rows from two or more tables based on related columns.

### INNER JOIN
Returns only rows where the join condition is met in **both** tables.

```sql
SELECT 
  customers.customer_id,
  customers.customer_name,
  orders.order_id,
  orders.order_date
FROM customers
INNER JOIN orders 
  ON customers.customer_id = orders.customer_id;
```

### LEFT JOIN (LEFT OUTER JOIN)
Returns all rows from the **left** table and matching rows from the right table.

```sql
SELECT 
  customers.customer_name,
  orders.order_id
FROM customers
LEFT JOIN orders 
  ON customers.customer_id = orders.customer_id;
-- Customers with no orders will still appear with NULL order_id
```

### RIGHT JOIN (RIGHT OUTER JOIN)
Returns all rows from the **right** table and matching rows from the left table.

```sql
SELECT 
  customers.customer_name,
  orders.order_id
FROM customers
RIGHT JOIN orders 
  ON customers.customer_id = orders.customer_id;
```

### FULL OUTER JOIN
Returns all rows from **both** tables, with NULLs where there's no match.

```sql
SELECT 
  customers.customer_name,
  orders.order_id
FROM customers
FULL OUTER JOIN orders 
  ON customers.customer_id = orders.customer_id;
```

### CROSS JOIN
Returns the Cartesian product (every combination).

```sql
SELECT * FROM colors CROSS JOIN sizes;
-- If colors has 3 rows and sizes has 4 rows, result has 12 rows
```

### Multiple JOINs
```sql
SELECT 
  c.customer_name,
  o.order_id,
  p.product_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN products p ON o.product_id = p.product_id;
```

---

## Aggregation & Grouping

### Aggregate Functions
| Function | Description | Example |
|----------|-------------|---------|
| `COUNT(*)` | Counts all rows | `COUNT(*)` |
| `COUNT(column)` | Counts non-NULL values | `COUNT(email)` |
| `SUM(column)` | Sum of values | `SUM(salary)` |
| `AVG(column)` | Average of values | `AVG(price)` |
| `MIN(column)` | Minimum value | `MIN(birth_date)` |
| `MAX(column)` | Maximum value | `MAX(salary)` |

### Examples
```sql
-- Count total employees
SELECT COUNT(*) FROM employees;

-- Average salary
SELECT AVG(salary) FROM employees;

-- Maximum order amount
SELECT MAX(total_amount) FROM orders;

-- Multiple aggregates
SELECT 
  COUNT(*) AS total_orders,
  SUM(total_amount) AS total_revenue,
  AVG(total_amount) AS average_order
FROM orders;
```

### GROUP BY
Groups rows that have the same values and applies aggregate functions.

```sql
-- Total sales by department
SELECT 
  department,
  COUNT(*) AS employee_count,
  AVG(salary) AS avg_salary
FROM employees
GROUP BY department;

-- Orders by customer
SELECT 
  customer_id,
  COUNT(*) AS order_count,
  SUM(total_amount) AS total_spent
FROM orders
GROUP BY customer_id;
```

### HAVING
Filters groups after aggregation (like WHERE but for groups).

```sql
-- Departments with average salary > $60,000
SELECT 
  department,
  AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;

-- Customers who spent more than $5,000
SELECT 
  customer_id,
  SUM(total_amount) AS total_spent
FROM orders
GROUP BY customer_id
HAVING SUM(total_amount) > 5000;
```

### ORDER BY
Sorts the result set.

```sql
-- Sort by salary ascending (default)
SELECT * FROM employees ORDER BY salary;

-- Sort by salary descending
SELECT * FROM employees ORDER BY salary DESC;

-- Sort by multiple columns
SELECT * FROM employees 
ORDER BY department, salary DESC;

-- With LIMIT (MySQL/SQLite) or FETCH (SQL Standard)
SELECT * FROM employees ORDER BY salary DESC LIMIT 10;
SELECT * FROM employees ORDER BY salary DESC FETCH FIRST 10 ROWS ONLY;
```

---

## Subqueries

A query nested inside another query.

### Scalar Subquery (returns single value)
```sql
-- Find employees earning more than average
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

### IN Subquery
```sql
-- Find customers who placed orders
SELECT * FROM customers
WHERE customer_id IN (SELECT DISTINCT customer_id FROM orders);
```

### EXISTS Subquery
```sql
-- Find customers with at least one order
SELECT * FROM customers c
WHERE EXISTS (
  SELECT 1 FROM orders o 
  WHERE o.customer_id = c.customer_id
);
```

### Correlated Subquery
The subquery references columns from the outer query.

```sql
-- Find employees earning more than their department average
SELECT * FROM employees e1
WHERE salary > (
  SELECT AVG(salary) 
  FROM employees e2 
  WHERE e2.department = e1.department
);
```

### FROM Subquery (Derived Table)
```sql
SELECT department, avg_salary
FROM (
  SELECT department, AVG(salary) AS avg_salary
  FROM employees
  GROUP BY department
) dept_avg
WHERE avg_salary > 50000;
```

---

## Data Modification

### INSERT
Adds new rows to a table.

```sql
-- Insert single row
INSERT INTO customers (customer_id, first_name, last_name, email)
VALUES (1, 'John', 'Doe', 'john@example.com');

-- Insert multiple rows
INSERT INTO customers (first_name, last_name, email) VALUES
('Jane', 'Smith', 'jane@example.com'),
('Bob', 'Johnson', 'bob@example.com');

-- Insert from SELECT
INSERT INTO customers_backup
SELECT * FROM customers WHERE country = 'USA';
```

### UPDATE
Modifies existing rows.

```sql
-- Update specific rows
UPDATE employees
SET salary = 75000
WHERE employee_id = 5;

-- Update with calculation
UPDATE products
SET price = price * 1.1
WHERE category = 'Electronics';

-- Update multiple columns
UPDATE employees
SET salary = 80000, department = 'Management'
WHERE employee_id = 5;

-- Update with condition
UPDATE orders
SET status = 'shipped'
WHERE order_date < '2025-10-01' AND status = 'processing';
```

### DELETE
Removes rows from a table.

```sql
-- Delete specific rows
DELETE FROM orders
WHERE order_id = 100;

-- Delete with condition
DELETE FROM customers
WHERE country = 'Deleted' AND email IS NULL;

-- Delete all rows (be careful!)
DELETE FROM temporary_table;
```

---

## Advanced Topics

### UNION
Combines results from multiple queries.

```sql
-- UNION: removes duplicates
SELECT first_name FROM employees
UNION
SELECT first_name FROM customers;

-- UNION ALL: keeps duplicates
SELECT first_name FROM employees
UNION ALL
SELECT first_name FROM customers;
```

### Common Table Expressions (CTE / WITH clause)
Makes complex queries more readable.

```sql
WITH high_earners AS (
  SELECT * FROM employees
  WHERE salary > 100000
)
SELECT department, COUNT(*)
FROM high_earners
GROUP BY department;

-- Multiple CTEs
WITH sales_data AS (
  SELECT * FROM orders WHERE status = 'shipped'
),
customer_totals AS (
  SELECT customer_id, SUM(total_amount) AS total
  FROM sales_data
  GROUP BY customer_id
)
SELECT c.customer_name, ct.total
FROM customers c
JOIN customer_totals ct ON c.customer_id = ct.customer_id;
```

### Window Functions
Performs calculations across rows while keeping row identity.

```sql
-- ROW_NUMBER: unique sequential number
SELECT 
  employee_id,
  salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- RANK: allows ties
SELECT 
  employee_id,
  salary,
  RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_salary_rank
FROM employees;

-- Running totals
SELECT 
  order_date,
  order_amount,
  SUM(order_amount) OVER (ORDER BY order_date) AS running_total
FROM orders;
```

### CASE Statement
Conditional logic within queries.

```sql
SELECT 
  employee_id,
  salary,
  CASE
    WHEN salary < 30000 THEN 'Junior'
    WHEN salary < 60000 THEN 'Mid-level'
    WHEN salary < 100000 THEN 'Senior'
    ELSE 'Executive'
  END AS salary_level
FROM employees;

-- Simple CASE
SELECT 
  country,
  CASE country
    WHEN 'USA' THEN 'North America'
    WHEN 'Canada' THEN 'North America'
    WHEN 'Mexico' THEN 'North America'
    ELSE 'Other'
  END AS region
FROM customers;
```

---

## Practice Problems

### Problem 1: Basic SELECT
**Question:** Write a query to get the first name and email of all customers from the USA.

<details>
<summary>Solution</summary>

```sql
SELECT first_name, email FROM customers
WHERE country = 'USA';
```

</details>

### Problem 2: JOIN
**Question:** Get the customer name and order count for customers who have placed more than 5 orders.

<details>
<summary>Solution</summary>

```sql
SELECT 
  c.customer_name,
  COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(o.order_id) > 5;
```

</details>

### Problem 3: Aggregation
**Question:** Find the average salary by department, but only for departments with more than 5 employees.

<details>
<summary>Solution</summary>

```sql
SELECT 
  department,
  AVG(salary) AS avg_salary,
  COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;
```

</details>

### Problem 4: Subquery
**Question:** List all products that are more expensive than the average product price.

<details>
<summary>Solution</summary>

```sql
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);
```

</details>

### Problem 5: Complex Query
**Question:** Find the top 3 customers by total spending.

<details>
<summary>Solution</summary>

```sql
SELECT 
  c.customer_id,
  c.customer_name,
  SUM(o.total_amount) AS total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 3;
```

</details>

---

## Tips & Best Practices

1. **Use Aliases**: Make queries readable with table and column aliases
2. **Indent Properly**: Format multi-line queries for clarity
3. **Use LIMIT**: Test queries with LIMIT before running on large datasets
4. **Comment Code**: Use `--` to add comments explaining complex logic
5. **Avoid SELECT ***: Specify columns to improve performance and clarity
6. **Test Incrementally**: Build complex queries step by step
7. **Understand NULL**: NULL is neither true nor false - handle it explicitly
8. **Use JOINs Over Subqueries**: Generally faster and more readable
9. **Index Foreign Keys**: Speed up JOIN operations
10. **Back Up Data**: Before DELETE or UPDATE operations

---

## SQL Dialects Reference

Different databases have slight syntax variations:

| Feature | MySQL | PostgreSQL | SQLite | SQL Server |
|---------|-------|-----------|--------|-----------|
| LIMIT | LIMIT 10 | LIMIT 10 | LIMIT 10 | TOP 10 |
| Auto-increment | AUTO_INCREMENT | SERIAL | AUTOINCREMENT | IDENTITY |
| String concat | CONCAT() | \|\| | \|\| | + |
| Substring | SUBSTRING() | SUBSTRING() | SUBSTR() | SUBSTRING() |
| Current date | NOW() | NOW() | DATE('now') | GETDATE() |

---

## Resources for Further Learning

- [SQL Tutorial by W3Schools](https://www.w3schools.com/sql/)
- [Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)
- [LeetCode Database Problems](https://leetcode.com/problemset/database/)
- [HackerRank SQL Challenges](https://www.hackerrank.com/domains/sql)

---

**Good luck with your database class! Remember, the best way to learn SQL is by practicing with real data.**
