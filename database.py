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

    # Create tables
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

    # Ensure 'encoded_by' column exists in 'bookings'
    cursor.execute("PRAGMA table_info(bookings)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'encoded_by' not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN encoded_by TEXT DEFAULT 'admin'")
        print("✅ Column 'encoded_by' successfully added to 'bookings' table.")
    else:
        print("ℹ️ Column 'encoded_by' already exists in 'bookings' table.")

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

def check_booking_conflict(room_no, new_checkin_dt, new_checkout_dt, booking_id_to_ignore=None):
    """Check for time overlap conflicts with existing bookings for the same room, excluding checked-out and the booking being modified."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, date, checkin_time, checkout_date, checkout_time, status
        FROM bookings
        WHERE room_no = ?
    """, (room_no,))
    bookings = cursor.fetchall()
    conn.close()

    for booking in bookings:
        existing_id = booking[0]
        existing_checkin_dt = datetime.strptime(f"{booking[1]} {booking[2]}", "%Y-%m-%d %H:%M")
        existing_checkout_dt = datetime.strptime(f"{booking[3]} {booking[4]}", "%Y-%m-%d %H:%M")
        existing_status = booking[5]

        # Skip if it's the same booking we're updating (early check-in or extension)
        if booking_id_to_ignore is not None and existing_id == booking_id_to_ignore:
            continue

        # Skip checked-out bookings
        if existing_status.lower() == "checked out":
            continue

        # Conflict detection
        if (new_checkin_dt < existing_checkout_dt) and (new_checkout_dt > existing_checkin_dt):
            return True  # Conflict detected

    return False  # No conflict



def save_booking(date, room_no, name, checkin, checkout_date, checkout_time, status):
    checkin_dt = datetime.strptime(f"{date} {checkin}", "%Y-%m-%d %H:%M")
    checkout_dt = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y-%m-%d %H:%M")

    if checkout_dt <= checkin_dt:
        checkout_dt += timedelta(days=1)

    # Check for conflicts
    if check_booking_conflict(room_no, checkin_dt, checkout_dt):
        return False  # Conflict detected, let GUI handle this gracefully

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
    result = cursor.fetchone()
    base_price = result[0] if result else 0

    duration_hours = max(1, (checkout_dt - checkin_dt).total_seconds() / 3600)
    blocks = int((duration_hours + 2.9) // 3)
    total_cost = base_price * blocks

    cursor.execute("""
        INSERT INTO bookings (date, room_no, customer_name, checkin_time, checkout_date, checkout_time, status, total_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost))
    conn.commit()
    conn.close()
    return True  # Booking successful


def save_booking_with_cost(date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost):
    checkin_dt = datetime.strptime(f"{date} {checkin}", "%Y-%m-%d %H:%M")
    checkout_dt = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y-%m-%d %H:%M")

    if checkout_dt <= checkin_dt:
        checkout_dt += timedelta(days=1)

    if check_booking_conflict(room_no, checkin_dt, checkout_dt):
        return False  # Conflict detected

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bookings (date, room_no, customer_name, checkin_time, checkout_date, checkout_time, status, total_cost)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, room_no, name, checkin, checkout_date, checkout_time, status, total_cost))
    conn.commit()
    conn.close()
    return True  # Booking saved




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

def add_room(room_no, base_price):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO room_prices (room_no, base_price)
            VALUES (?, ?)
        """, (room_no, base_price))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def remove_room(room_no):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM room_prices WHERE room_no = ?
    """, (room_no,))
    conn.commit()
    conn.close()

def update_room_price(room_no, new_base_price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE room_prices SET base_price = ?
        WHERE room_no = ?
    """, (new_base_price, room_no))
    conn.commit()
    conn.close()
    
def get_all_rooms_from_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT room_no FROM room_prices")
    rows = cursor.fetchall()
    conn.close()
    return [str(row[0]) for row in rows]  # Return room numbers as strings

def get_room_statuses_for_date(date):
    all_rooms = get_all_rooms_from_db()
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch bookings that overlap this date
    cursor.execute("""
        SELECT room_no, status
        FROM bookings
        WHERE date <= ? AND checkout_date >= ?
    """, (date, date))
    records = cursor.fetchall()
    conn.close()

    room_status = {room: "vacant" for room in all_rooms}

    for room_no, status in records:
        status_lower = status.lower()
        if status_lower == "checked in":
            room_status[room_no] = "occupied"  # Show as 'occupied' in Room Map
        elif status_lower == "reserved":
            room_status[room_no] = "reserved"  # Show as 'reserved' in Room Map
        # If 'checked out', do nothing — room stays 'vacant' in the map

    return room_status, all_rooms


    # Fetch bookings that overlap this date
    cursor.execute("""
        SELECT room_no, status
        FROM bookings
        WHERE date <= ? AND checkout_date >= ?
    """, (date, date))
    records = cursor.fetchall()
    conn.close()

    room_status = {room: "vacant" for room in all_rooms}

    for room_no, status in records:
        room_status[room_no] = status.lower()

    return room_status, all_rooms

