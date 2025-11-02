# SQLite3 Practice Database Guide

## Quick Start

### 1. Generate the Sample Database

Run the setup script to create `sample.db`:

```bash
python3 setup_sample_db.py
```

This creates a SQLite database with realistic sample data across 6 tables.

### 2. Open the Database

```bash
sqlite3 sample.db
```

Once inside sqlite3, you can:
- `.tables` - list all tables
- `.schema` - show table structure
- `.mode column` - display results in columns
- `.headers on` - show column headers
- `.exit` - quit

### 3. Practice Queries

Try the example queries below!

---

## Database Schema

### Customers Table
Stores customer information.

```
customer_id (PRIMARY KEY)
first_name
last_name
email (UNIQUE)
country
created_date
```

### Products Table
Inventory of products available for purchase.

```
product_id (PRIMARY KEY)
product_name
category
price
stock_quantity
```

### Orders Table
Customer orders with total amounts and status.

```
order_id (PRIMARY KEY)
customer_id (FOREIGN KEY → customers)
order_date
total_amount
status (shipped, processing, pending)
```

### Order_Items Table
Junction table linking orders to products with quantities.

```
order_item_id (PRIMARY KEY)
order_id (FOREIGN KEY → orders)
product_id (FOREIGN KEY → products)
quantity
unit_price
```

### Employees Table
Employee information by department.

```
employee_id (PRIMARY KEY)
first_name
last_name
department
salary
hire_date
```

### Reviews Table
Customer product reviews and ratings.

```
review_id (PRIMARY KEY)
customer_id (FOREIGN KEY → customers)
product_id (FOREIGN KEY → products)
rating (1-5)
review_text
review_date
```

---

## Practice Queries

### INNER JOIN Queries

#### 1. Get all customers with their orders
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id;
```

**What it shows:** Only customers who have placed at least one order.

#### 2. Get customer names and products they ordered
```sql
SELECT DISTINCT
    c.first_name,
    c.last_name,
    p.product_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY c.first_name, p.product_name;
```

**What it shows:** Who bought what (with multiple JOINs).

#### 3. Get order details with product names and quantities
```sql
SELECT 
    o.order_id,
    c.first_name,
    c.last_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id, p.product_name;
```

**What it shows:** Full order details with all related information.

---

### LEFT JOIN Queries

#### 4. Get all customers, even those without orders
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC NULLS LAST;
```

**What it shows:** All customers including Eve Miller who has no orders (NULL values).

#### 5. Get products and their review count
```sql
SELECT 
    p.product_id,
    p.product_name,
    p.price,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name, p.price
ORDER BY avg_rating DESC NULLS LAST;
```

**What it shows:** All products and their ratings (even products with no reviews).

#### 6. Get customers and their latest order
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    MAX(o.order_date) AS latest_order,
    COUNT(o.order_id) AS total_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY latest_order DESC NULLS LAST;
```

**What it shows:** When each customer made their last order.

---

### Aggregation with JOINs

#### 7. Total sales by customer
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS avg_order_value
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_revenue DESC;
```

**What it shows:** Customer spending patterns.

#### 8. Revenue by product category
```sql
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) AS product_count,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.quantity * oi.unit_price) AS avg_line_value
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;
```

**What it shows:** Which product categories generate the most revenue.

#### 9. Top products by quantity sold
```sql
SELECT 
    p.product_id,
    p.product_name,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity_sold DESC;
```

**What it shows:** Best-selling products and their ratings.

---

### Subqueries with JOINs

#### 10. Customers who spent more than average
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.total_amount) AS total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING SUM(o.total_amount) > (
    SELECT AVG(total) FROM (
        SELECT SUM(total_amount) AS total
        FROM orders
        GROUP BY customer_id
    )
)
ORDER BY total_spent DESC;
```

**What it shows:** High-value customers.

#### 11. Products never reviewed
```sql
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price
FROM products p
WHERE p.product_id NOT IN (
    SELECT DISTINCT product_id FROM reviews
)
ORDER BY p.product_name;
```

**What it shows:** Which products need more customer feedback.

---

### Set Operations

#### 12. UNION - Customers AND employees combined
```sql
SELECT 'Customer' AS type, first_name, last_name, NULL AS department
FROM customers
UNION
SELECT 'Employee' AS type, first_name, last_name, department
FROM employees
ORDER BY type, last_name;
```

**What it shows:** All people in the database from both tables.

---

### Window Functions (Advanced)

#### 13. Rank products by review rating
```sql
SELECT 
    product_id,
    product_name,
    avg_rating,
    RANK() OVER (ORDER BY avg_rating DESC) AS rating_rank
FROM (
    SELECT 
        p.product_id,
        p.product_name,
        ROUND(AVG(r.rating), 2) AS avg_rating
    FROM products p
    LEFT JOIN reviews r ON p.product_id = r.product_id
    GROUP BY p.product_id, p.product_name
)
WHERE avg_rating IS NOT NULL
ORDER BY rating_rank;
```

**What it shows:** Product rankings by customer satisfaction.

---

## Challenge Queries

Try these challenging queries to test your skills:

### Challenge 1: Customer lifetime value
Find the customer with the highest lifetime value, including their top 3 purchased products.

<details>
<summary>Hint</summary>
Use a CTE to calculate lifetime value, then JOIN with order details.
</details>

<details>
<summary>Solution</summary>

```sql
WITH customer_totals AS (
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        SUM(o.total_amount) AS lifetime_value
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
)
SELECT 
    ct.customer_id,
    ct.first_name,
    ct.last_name,
    ct.lifetime_value,
    p.product_name,
    SUM(oi.quantity) AS qty_purchased
FROM customer_totals ct
INNER JOIN orders o ON ct.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE ct.lifetime_value = (SELECT MAX(lifetime_value) FROM customer_totals)
GROUP BY p.product_id, p.product_name
ORDER BY qty_purchased DESC
LIMIT 3;
```

</details>

### Challenge 2: Products by satisfaction vs. sales
Find products with high ratings but low sales (opportunity to market better).

<details>
<summary>Hint</summary>
Use LEFT JOINs to get all products, then filter by average rating and total quantity sold.
</details>

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.product_id,
    p.product_name,
    p.price,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(DISTINCT r.review_id) AS review_count,
    SUM(oi.quantity) AS total_sold
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.price
HAVING ROUND(AVG(r.rating), 2) >= 4.5 
   AND SUM(oi.quantity) < 5
ORDER BY avg_rating DESC, total_sold;
```

</details>

---

## Debugging Tips

### View your data first
Always use simple SELECT queries to understand your data:

```sql
SELECT * FROM customers LIMIT 5;
SELECT * FROM orders WHERE customer_id = 1;
```

### Use WHERE to test joins
Test your JOIN logic with a WHERE clause before aggregating:

```sql
SELECT * FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id = 1;
```

### Check for NULL values
Don't forget that NULL != NULL:

```sql
SELECT * FROM customers WHERE created_date IS NULL;
```

### Count before aggregating
Make sure you understand what you're counting:

```sql
SELECT COUNT(*) FROM orders;
SELECT COUNT(DISTINCT customer_id) FROM orders;
```

---

## Next Steps

Once you've mastered these queries:

1. **Modify the data**: Add your own customers, products, and orders
2. **Create views**: Practice `CREATE VIEW` for frequently-used queries
3. **Add indexes**: Learn about performance with `CREATE INDEX`
4. **Try transactions**: Practice `BEGIN`, `COMMIT`, `ROLLBACK`
5. **Write triggers**: Explore automated actions with `CREATE TRIGGER`

---

Happy practicing! 🚀
