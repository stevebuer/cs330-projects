# Quick Reference: SQLite3 Practice Database

## Database Setup

```bash
# Create the database with sample data
python3 setup_sample_db.py

# Open the database
sqlite3 sample.db

# Useful SQLite commands
.tables              # List all tables
.schema              # Show all table definitions
.schema customers    # Show specific table structure
.mode column         # Display results in columns
.headers on          # Show column headers
.quit                # Exit SQLite
```

## Database Overview

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **customers** | Customer information | customer_id, first_name, last_name, email, country |
| **products** | Available products | product_id, product_name, category, price, stock_quantity |
| **orders** | Customer orders | order_id, customer_id, order_date, total_amount, status |
| **order_items** | Order line items | order_item_id, order_id, product_id, quantity, unit_price |
| **employees** | Employee data | employee_id, first_name, last_name, department, salary |
| **reviews** | Product reviews | review_id, customer_id, product_id, rating, review_text |

## Key Relationships

```
customers (1) ──── (M) orders
customers (1) ──── (M) reviews
products (1) ──── (M) reviews
products (1) ──── (M) order_items
orders (1) ──── (M) order_items
```

## One-Minute Learning: JOINs Explained

### INNER JOIN ✓
**Shows:** Matching records from BOTH tables only
```sql
SELECT * FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;
```
Result: Only customers WITH orders

### LEFT JOIN ✓
**Shows:** ALL from LEFT table + matches from RIGHT
```sql
SELECT * FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```
Result: ALL customers (including Eve with no orders → NULL)

### RIGHT JOIN ✓
**Shows:** Matches from LEFT + ALL from RIGHT
```sql
SELECT * FROM orders o
RIGHT JOIN customers c ON o.customer_id = c.customer_id;
```
Result: Same as LEFT JOIN but table order matters

### FULL OUTER JOIN ✓
**Shows:** ALL from both tables
```sql
SELECT * FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
```
Result: All customers + all orders (some with NULL values)

---

## Essential Practice Queries

### 1. See Basic Data
```sql
SELECT * FROM customers LIMIT 5;
SELECT * FROM products;
SELECT * FROM orders;
```

### 2. Simple INNER JOIN
```sql
SELECT c.first_name, o.order_id, o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.first_name;
```

### 3. Simple LEFT JOIN (Key for learning!)
```sql
SELECT c.first_name, COUNT(o.order_id) as num_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY c.first_name;
```
⭐ **Notice:** Eve Miller shows with 0 orders

### 4. Multiple JOINs (What did each customer buy?)
```sql
SELECT c.first_name, p.product_name, oi.quantity
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY c.first_name, p.product_name;
```

### 5. Aggregation (How much did each customer spend?)
```sql
SELECT 
    c.first_name,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC NULLS LAST;
```

---

## Common Mistakes to Avoid

### ❌ Missing ON clause
```sql
-- WRONG: Returns Cartesian product (all combinations)
SELECT * FROM customers, orders;
```

### ✓ Correct
```sql
-- RIGHT: Specifies relationship
SELECT * FROM customers
INNER JOIN orders ON customers.customer_id = orders.customer_id;
```

---

### ❌ Forgetting GROUP BY with aggregates
```sql
-- WRONG: Ambiguous which first_name to show
SELECT first_name, SUM(total_amount)
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```

### ✓ Correct
```sql
-- RIGHT: Specifies grouping
SELECT c.first_name, SUM(o.total_amount)
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name;
```

---

### ❌ WHERE vs HAVING
```sql
-- WRONG: Filters before aggregation
SELECT dept, SUM(salary)
FROM employees
WHERE SUM(salary) > 100000
GROUP BY dept;
```

### ✓ Correct
```sql
-- RIGHT: Filters after aggregation
SELECT dept, SUM(salary) as total_salary
FROM employees
GROUP BY dept
HAVING SUM(salary) > 100000;
```

---

## Data Overview

### Sample Data Statistics
- **Customers:** 7 total (1 with no orders)
- **Products:** 8 products in 3 categories
- **Orders:** 8 orders with various statuses
- **Order Items:** 12 line items across orders
- **Employees:** 5 employees in 3 departments
- **Reviews:** 7 product reviews

### Why This Sample is Good for Learning
✓ Small enough to understand easily  
✓ Has NULLs (Eve's created_date, customers with no orders)  
✓ Has duplicates for aggregation practice  
✓ Multiple relationships for JOIN practice  
✓ Mix of numeric and text data  

---

## Progressive Learning Path

### Day 1: Basic SELECT & WHERE
```sql
SELECT * FROM customers WHERE country = 'USA';
SELECT * FROM orders WHERE total_amount > 500;
SELECT DISTINCT category FROM products;
```

### Day 2: JOINs
```sql
-- Start simple
SELECT * FROM customers INNER JOIN orders ...

-- Then aggregate
SELECT c.first_name, COUNT(o.order_id) FROM customers c
LEFT JOIN orders o ...

-- Then add more JOINs
SELECT ... FROM customers c
INNER JOIN orders o ...
INNER JOIN order_items oi ...
INNER JOIN products p ...
```

### Day 3: Subqueries & Advanced
```sql
SELECT * FROM products
WHERE product_id IN (SELECT product_id FROM reviews);

WITH customer_totals AS (...)
SELECT * FROM customer_totals ...
```

---

## Helpful Resources in This Directory

1. **README.md** - Full SQL study guide with all concepts
2. **PRACTICE_GUIDE.md** - Detailed practice queries with explanations
3. **setup_sample_db.py** - Script to create the database
4. **sample.db** - The actual SQLite database file (created after running setup script)

---

## Useful SQLite Tips

### Export query results to CSV
```bash
sqlite3 sample.db ".mode csv" ".headers on" ".output results.csv" \
  "SELECT * FROM orders;" ".quit"
```

### Backup database
```bash
cp sample.db sample_backup.db
```

### Reset database
```bash
python3 setup_sample_db.py  # Re-run setup script
```

### View data in readable format
```bash
sqlite3 sample.db
sqlite> .mode column
sqlite> .headers on
sqlite> SELECT * FROM customers;
```

---

**Quick Start:** `python3 setup_sample_db.py && sqlite3 sample.db`

Then try: `SELECT * FROM customers;` and start experimenting! 🚀
