# database.py

import sqlite3

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

    # Create bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        room_no TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        checkin_time TEXT NOT NULL,
        checkout_time TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'cashier'))
    )
    """)
def save_booking(date, room_no, name, checkin, checkout, status):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO bookings (date, room_no, customer_name, checkin_time, checkout_time, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (date, room_no, name, checkin, checkout, status))

    conn.commit()
    conn.close()
