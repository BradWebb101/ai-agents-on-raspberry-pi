import sqlite3
import os
import random
import string

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/sqlite/database.db')

# Table definitions for an e-commerce business
TABLES = {
    'products': [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('name', 'TEXT'),
        ('price', 'REAL'),
        ('in_stock', 'BOOLEAN'),
        ('category', 'TEXT'),
    ],
    'customers': [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('first_name', 'TEXT'),
        ('last_name', 'TEXT'),
        ('email', 'TEXT'),
        ('is_active', 'BOOLEAN'),
    ],
    'orders': [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('customer_id', 'INTEGER'),
        ('order_date', 'TEXT'),
        ('total_amount', 'REAL'),
        ('is_paid', 'BOOLEAN'),
    ],
    'order_items': [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('order_id', 'INTEGER'),
        ('product_id', 'INTEGER'),
        ('quantity', 'INTEGER'),
        ('is_gift', 'BOOLEAN'),
    ],
    'employees': [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('first_name', 'TEXT'),
        ('last_name', 'TEXT'),
        ('department', 'TEXT'),
        ('is_manager', 'BOOLEAN'),
    ],
}

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_email():
    return f"{random_string(5).lower()}@{random_string(5).lower()}.com"

def create_tables(conn):
    for table, columns in TABLES.items():
        col_defs = ', '.join([f"{name} {type}" for name, type in columns])
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} ({col_defs})")
    conn.commit()

def insert_dummy_data(conn):
    for table, columns in TABLES.items():
        col_names = [name for name, _ in columns if name != 'id']
        for i in range(100):
            if table == 'products':
                values = [
                    random_string(10),  # name
                    round(random.uniform(5, 500), 2),  # price
                    random.choice([0, 1]),  # in_stock
                    random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Toys']),  # category
                ]
            elif table == 'customers':
                values = [
                    random_string(6),  # first_name
                    random_string(8),  # last_name
                    random_email(),  # email
                    random.choice([0, 1]),  # is_active
                ]
            elif table == 'orders':
                values = [
                    random.randint(1, 100),  # customer_id
                    f"2024-06-{random.randint(1, 28):02d}",  # order_date
                    round(random.uniform(20, 2000), 2),  # total_amount
                    random.choice([0, 1]),  # is_paid
                ]
            elif table == 'order_items':
                values = [
                    random.randint(1, 100),  # order_id
                    random.randint(1, 100),  # product_id
                    random.randint(1, 10),  # quantity
                    random.choice([0, 1]),  # is_gift
                ]
            elif table == 'employees':
                values = [
                    random_string(6),  # first_name
                    random_string(8),  # last_name
                    random.choice(['Sales', 'Support', 'IT', 'HR', 'Logistics']),  # department
                    random.choice([0, 1]),  # is_manager
                ]
            else:
                values = [None] * (len(col_names))
            placeholders = ','.join(['?'] * len(values))
            conn.execute(f"INSERT INTO {table} ({','.join(col_names)}) VALUES ({placeholders})", values)
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    insert_dummy_data(conn)
    conn.close()
    print("Dummy e-commerce data inserted.")

if __name__ == "__main__":
    main()
