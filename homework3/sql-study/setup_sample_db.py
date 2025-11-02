#!/usr/bin/env python3
"""
SQLite3 Sample Database Setup Script
Creates a practice database with sample tables for learning SQL queries
"""

import sqlite3
import os
from datetime import datetime, timedelta

def create_database(db_name='sample.db'):
    """Create and initialize the sample database"""
    
    # Remove existing database if it exists
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Removed existing {db_name}")
    
    # Connect to database (creates it if doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print(f"Creating database: {db_name}\n")
    
    # Create tables
    create_tables(cursor)
    
    # Insert sample data
    insert_sample_data(cursor)
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print(f"\n✓ Database '{db_name}' created successfully!")
    print("You can now practice queries using: sqlite3 sample.db")

def create_tables(cursor):
    """Create sample tables"""
    
    print("Creating tables...")
    
    # Customers table
    cursor.execute('''
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        country TEXT,
        created_date DATE
    )
    ''')
    print("  ✓ customers table created")
    
    # Products table
    cursor.execute('''
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT,
        price DECIMAL(10, 2),
        stock_quantity INTEGER
    )
    ''')
    print("  ✓ products table created")
    
    # Orders table
    cursor.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date DATE,
        total_amount DECIMAL(10, 2),
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')
    print("  ✓ orders table created")
    
    # Order_items table (junction table)
    cursor.execute('''
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER,
        unit_price DECIMAL(10, 2),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')
    print("  ✓ order_items table created")
    
    # Employees table
    cursor.execute('''
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        department TEXT,
        salary DECIMAL(10, 2),
        hire_date DATE
    )
    ''')
    print("  ✓ employees table created")
    
    # Reviews table
    cursor.execute('''
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        review_text TEXT,
        review_date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')
    print("  ✓ reviews table created")

def insert_sample_data(cursor):
    """Insert sample data into tables"""
    
    print("\nInserting sample data...")
    
    # Sample customers
    customers = [
        (1, 'John', 'Doe', 'john.doe@email.com', 'USA', '2024-01-15'),
        (2, 'Jane', 'Smith', 'jane.smith@email.com', 'USA', '2024-02-20'),
        (3, 'Bob', 'Johnson', 'bob.johnson@email.com', 'Canada', '2024-03-10'),
        (4, 'Alice', 'Williams', 'alice.williams@email.com', 'UK', '2024-04-05'),
        (5, 'Charlie', 'Brown', 'charlie.brown@email.com', 'USA', '2024-05-12'),
        (6, 'Diana', 'Davis', 'diana.davis@email.com', 'Australia', '2024-06-18'),
        (7, 'Eve', 'Miller', 'eve.miller@email.com', 'USA', None),  # Customer with no orders
    ]
    cursor.executemany('''
    INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)
    ''', customers)
    print(f"  ✓ Inserted {len(customers)} customers")
    
    # Sample products
    products = [
        (1, 'Laptop Pro', 'Electronics', 1299.99, 15),
        (2, 'USB-C Cable', 'Electronics', 19.99, 100),
        (3, 'Wireless Mouse', 'Electronics', 49.99, 45),
        (4, 'Monitor 27"', 'Electronics', 399.99, 20),
        (5, 'Desk Chair', 'Furniture', 249.99, 30),
        (6, 'Standing Desk', 'Furniture', 599.99, 10),
        (7, 'Desk Lamp', 'Furniture', 79.99, 50),
        (8, 'Coffee Maker', 'Appliances', 89.99, 25),
    ]
    cursor.executemany('''
    INSERT INTO products VALUES (?, ?, ?, ?, ?)
    ''', products)
    print(f"  ✓ Inserted {len(products)} products")
    
    # Sample orders
    orders = [
        (1, 1, '2024-09-01', 1319.98, 'shipped'),
        (2, 1, '2024-09-15', 49.99, 'shipped'),
        (3, 2, '2024-09-10', 2499.96, 'shipped'),
        (4, 2, '2024-10-01', 79.99, 'processing'),
        (5, 3, '2024-10-05', 399.99, 'shipped'),
        (6, 4, '2024-10-08', 1899.97, 'pending'),
        (7, 5, '2024-10-12', 249.99, 'shipped'),
        (8, 6, '2024-10-15', 599.99, 'shipped'),
        # Note: Customer 7 (Eve Miller) has no orders - good for LEFT JOIN practice
    ]
    cursor.executemany('''
    INSERT INTO orders VALUES (?, ?, ?, ?, ?)
    ''', orders)
    print(f"  ✓ Inserted {len(orders)} orders")
    
    # Sample order items
    order_items = [
        (1, 1, 1, 1, 1299.99),  # Order 1: 1x Laptop Pro
        (2, 1, 2, 1, 19.99),    # Order 1: 1x USB-C Cable
        (3, 2, 3, 1, 49.99),    # Order 2: 1x Wireless Mouse
        (4, 3, 1, 1, 1299.99),  # Order 3: 1x Laptop Pro
        (5, 3, 4, 1, 399.99),   # Order 3: 1x Monitor
        (6, 3, 7, 1, 79.99),    # Order 3: 1x Desk Lamp
        (7, 4, 7, 1, 79.99),    # Order 4: 1x Desk Lamp
        (8, 5, 4, 1, 399.99),   # Order 5: 1x Monitor
        (9, 6, 1, 1, 1299.99),  # Order 6: 1x Laptop Pro
        (10, 6, 5, 1, 599.98),  # Order 6: 2x Desk Chair
        (11, 7, 5, 1, 249.99),  # Order 7: 1x Desk Chair
        (12, 8, 6, 1, 599.99),  # Order 8: 1x Standing Desk
    ]
    cursor.executemany('''
    INSERT INTO order_items VALUES (?, ?, ?, ?, ?)
    ''', order_items)
    print(f"  ✓ Inserted {len(order_items)} order items")
    
    # Sample employees
    employees = [
        (1, 'Alice', 'Manager', 'Sales', 75000.00, '2020-01-10'),
        (2, 'Bob', 'Engineer', 'IT', 85000.00, '2021-03-15'),
        (3, 'Carol', 'Analyst', 'Sales', 65000.00, '2022-06-20'),
        (4, 'David', 'Developer', 'IT', 90000.00, '2019-11-01'),
        (5, 'Eve', 'Specialist', 'HR', 70000.00, '2023-01-15'),
    ]
    cursor.executemany('''
    INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)
    ''', employees)
    print(f"  ✓ Inserted {len(employees)} employees")
    
    # Sample reviews
    reviews = [
        (1, 1, 1, 5, 'Excellent laptop! Very fast and reliable.', '2024-09-05'),
        (2, 2, 1, 5, 'Great performance. Highly recommended!', '2024-09-20'),
        (3, 1, 3, 4, 'Good mouse, comfortable to use.', '2024-09-16'),
        (4, 3, 4, 4, 'Nice monitor, good color accuracy.', '2024-10-10'),
        (5, 4, 1, 3, 'Good laptop but a bit pricey.', '2024-10-12'),
        (6, 5, 5, 5, 'Very comfortable desk chair!', '2024-10-15'),
        (7, 2, 7, 4, 'Good lamp, provides nice lighting.', '2024-10-05'),
    ]
    cursor.executemany('''
    INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?)
    ''', reviews)
    print(f"  ✓ Inserted {len(reviews)} reviews")

def main():
    """Main function"""
    db_name = 'sample.db'
    
    try:
        create_database(db_name)
        print("\n" + "="*60)
        print("Sample database ready for practice!")
        print("="*60)
        print("\nTry these queries to practice JOINs:\n")
        print("1. INNER JOIN (customers with orders):")
        print("   SELECT c.first_name, c.last_name, o.order_id")
        print("   FROM customers c")
        print("   INNER JOIN orders o ON c.customer_id = o.customer_id;\n")
        
        print("2. LEFT JOIN (all customers, even without orders):")
        print("   SELECT c.first_name, c.last_name, COUNT(o.order_id)")
        print("   FROM customers c")
        print("   LEFT JOIN orders o ON c.customer_id = o.customer_id")
        print("   GROUP BY c.customer_id;\n")
        
        print("3. Multiple JOINs:")
        print("   SELECT c.first_name, p.product_name, oi.quantity")
        print("   FROM customers c")
        print("   INNER JOIN orders o ON c.customer_id = o.customer_id")
        print("   INNER JOIN order_items oi ON o.order_id = oi.order_id")
        print("   INNER JOIN products p ON oi.product_id = p.product_id;\n")
        
        print("4. Aggregation with JOIN and GROUP BY:")
        print("   SELECT c.first_name, COUNT(o.order_id) as order_count,")
        print("          SUM(o.total_amount) as total_spent")
        print("   FROM customers c")
        print("   LEFT JOIN orders o ON c.customer_id = o.customer_id")
        print("   GROUP BY c.customer_id;\n")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
