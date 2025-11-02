# SQL Study Directory - Getting Started

Welcome to your SQL learning workspace! 🎓

## What You Have

This directory contains everything you need to master SQL, with a focus on JOINs and practical database work:

### 📚 Learning Materials

1. **README.md** (15 KB)
   - Comprehensive SQL study guide
   - Topics: Fundamentals, SELECT, WHERE, JOINs, Aggregation, Subqueries, Data Modification, Advanced Topics
   - Includes practice problems with solutions
   - Best practices and SQL dialect reference

2. **QUICK_REFERENCE.md** (6.7 KB)
   - One-page cheat sheet for quick lookup
   - Focus on JOINs (INNER, LEFT, RIGHT, FULL, CROSS)
   - Common mistakes and how to avoid them
   - Progressive learning path (3-day plan)

3. **PRACTICE_GUIDE.md** (11 KB)
   - Hands-on practice queries organized by difficulty
   - 13 different query examples with explanations
   - Challenge problems with solutions
   - Debugging tips

### 🗄️ Sample Database

4. **sample.db** (32 KB)
   - Pre-populated SQLite database
   - 6 tables with realistic data:
     - customers (7 records, including 1 with no orders for JOIN practice)
     - products (8 products in 3 categories)
     - orders (8 orders with various statuses)
     - order_items (junction table with 12 items)
     - employees (5 employees in 3 departments)
     - reviews (7 product reviews)

### 🛠️ Setup Tool

5. **setup_sample_db.py** (9.2 KB)
   - Python script to create the database from scratch
   - Can be run anytime to reset the database
   - Includes helpful suggestions for JOIN queries

## Quick Start

### Option 1: Use Pre-Built Database
The sample.db file is already created and ready to use!

```bash
sqlite3 sample.db
```

Then try:
```sql
.mode column
.headers on
SELECT * FROM customers;
```

### Option 2: Create Fresh Database
```bash
python3 setup_sample_db.py
```

This will:
- Remove old sample.db if it exists
- Create a new database
- Populate all tables with sample data
- Display suggestions for practice queries

## Recommended Learning Path

### Phase 1: Understand the Data (15 minutes)
```bash
sqlite3 sample.db
.mode column
.headers on
SELECT * FROM customers;
SELECT * FROM orders;
SELECT * FROM order_items;
SELECT * FROM products;
```

Refer to **QUICK_REFERENCE.md** for table relationships.

### Phase 2: Learn JOINs (30-45 minutes)
Follow the "One-Minute Learning: JOINs Explained" section in **QUICK_REFERENCE.md**

Try the essential practice queries:
1. Simple INNER JOIN
2. Simple LEFT JOIN  
3. Multiple JOINs
4. Aggregation with JOINs

### Phase 3: Practice & Challenge (1+ hours)
Work through queries in **PRACTICE_GUIDE.md**:
- INNER JOIN Queries (3 queries)
- LEFT JOIN Queries (3 queries)
- Aggregation with JOINs (3 queries)
- Subqueries with JOINs (2 queries)
- Challenge Problems (2 challenging problems)

### Phase 4: Deep Learning (Ongoing)
- Read explanations in **README.md** for concepts you're unsure about
- Modify the sample data and create your own queries
- Experiment with UPDATE, DELETE, INSERT operations
- Try creating VIEWs and INDEXes

## Key Features of This Setup

✅ **Small, manageable dataset** - Easy to understand while being realistic
✅ **Relationships** - All types of JOINs possible (1-to-many, many-to-many)
✅ **NULL values** - Learn how to handle missing data (Eve has no orders)
✅ **Multiple tables** - Practice complex queries with 4+ table JOINs
✅ **Aggregation** - Learn GROUP BY and HAVING with the data
✅ **Mix of data types** - Dates, decimals, text, integers
✅ **Business context** - e-commerce scenario is relatable and realistic

## Common SQLite Commands

```bash
sqlite3 sample.db                  # Open database
.tables                            # List tables
.schema                            # Show all table definitions
.schema customers                  # Show customers table structure
.mode column                       # Pretty column display
.headers on                        # Show column names
.quit                              # Exit SQLite

# Export data
.output results.csv
.mode csv
SELECT * FROM orders;
.quit

# Run from command line
sqlite3 sample.db "SELECT * FROM customers;"
sqlite3 sample.db < queries.sql   # Run SQL file
```

## Examples You Should Try

### Find customers who haven't placed orders yet
```sql
SELECT * FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```
Expected: Only Eve Miller

### Show all orders with customer and product names
```sql
SELECT c.first_name, p.product_name, oi.quantity, o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_date;
```

### Calculate total spending per customer
```sql
SELECT c.first_name, c.last_name, 
       COUNT(DISTINCT o.order_id) as order_count,
       SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC NULLS LAST;
```

## Next Steps After Mastering Basics

1. **Data Modification**: Try INSERT, UPDATE, DELETE
2. **Transactions**: Learn BEGIN, COMMIT, ROLLBACK
3. **Views**: Create VIEW for reusable queries
4. **Indexes**: Improve performance with CREATE INDEX
5. **Triggers**: Automate actions with CREATE TRIGGER
6. **More complex queries**: Window functions, recursive CTEs

## Tips for Success

- 📖 Read the material BEFORE trying queries
- 🔬 Start with simple SELECT to understand data
- 📝 Write down what each JOIN does before running it
- 🧪 Test queries incrementally (add one more table at a time)
- 💾 Backup your database before modifying data
- 🔄 Use `python3 setup_sample_db.py` to reset if you break something

## Resources

- **README.md** - Full reference for all SQL concepts
- **QUICK_REFERENCE.md** - Quick lookup, focus on JOINs
- **PRACTICE_GUIDE.md** - Hands-on practice with solutions
- SQLite Documentation: https://www.sqlite.org/docs.html

---

**You're all set! Start with `.tables` and `SELECT * FROM customers;`** 🚀

Questions? Check the relevant guide or re-read the schema section in QUICK_REFERENCE.md.

Good luck with your database class! 📚
