# fix_database.py

import sqlite3

DB_NAME = "hotel.db"

def add_encoded_by_column():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if 'encoded_by' column exists
    cursor.execute("PRAGMA table_info(bookings)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'encoded_by' not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN encoded_by TEXT DEFAULT 'admin'")
        print("✅ Column 'encoded_by' successfully added to 'bookings' table.")
    else:
        print("ℹ️ Column 'encoded_by' already exists in 'bookings' table.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_encoded_by_column()
