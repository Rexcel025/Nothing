#database.py
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "hotel.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(username, password, role):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (username, password, role))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        room_no TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        checkin_time TEXT NOT NULL,
        checkout_date TEXT NOT NULL,
        checkout_time TEXT NOT NULL,
        status TEXT NOT NULL,
        total_cost REAL DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'cashier'))
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS room_prices (
        room_no TEXT PRIMARY KEY,
        base_price REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

def seed_initial_data():
    conn = connect_db()
    cursor = conn.cursor()
    room_data = [("101", 240), ("102", 240), ("103", 240), ("104", 240), ("105", 240), ("106", 300),
                ("201", 300), ("202", 300), ("301", 500), ("302", 500)]
    cursor.executemany("INSERT OR IGNORE INTO room_prices (room_no, base_price) VALUES (?, ?)", room_data)

    product_data = [("Mineral Water", 20), ("Towel Rental", 50), ("Extra Pillow", 30)]
    cursor.executemany("INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)", product_data)
    conn.commit()
    conn.close()

def save_booking(date, room_no, name, checkin, checkout_date, checkout_time, status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
    result = cursor.fetchone()
    base_price = result[0] if result else 0

    checkin_dt = datetime.strptime(f"{date} {checkin}", "%Y-%m-%d %H:%M")
    checkout_dt = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y-%m-%d %H:%M")

    if checkout_dt < checkin_dt:
        checkout_dt += timedelta(days=1)

    duration_hours = max(1, (checkout_dt - checkin_dt).total_seconds() / 3600)
    blocks = int((duration_hours + 2.9) // 3)
    total_cost = base_price * blocks

    cursor.execute("""
        INSERT INTO bookings (date, room_no, customer_name, checkin_time, checkout_date, checkout_time, status, total_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost))
    conn.commit()
    conn.close()

def save_booking_with_cost(date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bookings (date, room_no, customer_name, checkin_time, checkout_date, checkout_time, status, total_cost)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost))
    conn.commit()
    conn.close()



def get_all_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_booking_products(booking_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.id, products.name, products.price, booking_products.quantity
        FROM booking_products
        JOIN products ON booking_products.product_id = products.id
        WHERE booking_products.booking_id = ?
    """, (booking_id,))
    products = cursor.fetchall()
    conn.close()
    return products

def add_product_to_booking(booking_id, product_id, quantity=1):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, quantity FROM booking_products
        WHERE booking_id = ? AND product_id = ?
    """, (booking_id, product_id))
    result = cursor.fetchone()

    if result:
        new_quantity = result[1] + quantity
        cursor.execute("""
            UPDATE booking_products
            SET quantity = ?
            WHERE id = ?
        """, (new_quantity, result[0]))
    else:
        cursor.execute("""
            INSERT INTO booking_products (booking_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (booking_id, product_id, quantity))

    conn.commit()
    conn.close()

def remove_product_from_booking(booking_id, product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM booking_products
        WHERE booking_id = ? AND product_id = ?
    """, (booking_id, product_id))
    conn.commit()
    conn.close()

def update_product_quantity(booking_id, product_id, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    if quantity <= 0:
        remove_product_from_booking(booking_id, product_id)
    else:
        cursor.execute("""
            UPDATE booking_products
            SET quantity = ?
            WHERE booking_id = ? AND product_id = ?
        """, (quantity, booking_id, product_id))
    conn.commit()
    conn.close()

def update_booking_status(booking_id, status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bookings SET status = ? WHERE id = ?
    """, (status, booking_id))
    conn.commit()
    conn.close()

def update_booking_total_cost(booking_id, total_cost):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bookings SET total_cost = ? WHERE id = ?
    """, (total_cost, booking_id))
    conn.commit()
    conn.close()
