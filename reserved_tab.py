# reserved_tab.py
# This file implements the ReservedTab widget, which displays a list of reserved customers
# and allows the user to perform actions like early check-in, extending bookings, and checking out
# customers. It includes a table to show booking details and buttons for actions.
# It uses PyQt5 for the GUI and interacts with a SQLite database for booking management.
# It also includes functionality to check for booking conflicts when performing actions.
# The database operations are handled in the database.py file.
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, QDate, QTime
from datetime import datetime
from database import connect_db, check_booking_conflict

class ReservedTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        title = QLabel("Reserved Customers")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Date", "Room", "Name", "Check-In Time", "Check-Out Time",
            "Check-Out Date", "Status", "Total Cost", "Current Status"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)
        self.table.verticalHeader().setVisible(False)

        # Buttons
        button_layout = QHBoxLayout()
        early_checkin_btn = QPushButton("Early Check-In")
        early_checkin_btn.clicked.connect(self.early_checkin_selected)
        extend_btn = QPushButton("Extend Booking")
        extend_btn.clicked.connect(self.extend_selected)
        checkout_btn = QPushButton("Check Out")
        checkout_btn.clicked.connect(self.checkout_selected)
        button_layout.addWidget(early_checkin_btn)
        button_layout.addWidget(extend_btn)
        button_layout.addWidget(checkout_btn)
        self.layout.addLayout(button_layout)

        self.load_data()

    def load_data(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE status = 'reserved'")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        now = datetime.now()

        for row in rows:
            check_in_dt = datetime.strptime(f"{row[1]} {row[4]}", "%Y-%m-%d %H:%M")
            check_out_dt = datetime.strptime(f"{row[5]} {row[6]}", "%Y-%m-%d %H:%M")
            current_status = "Overstayed" if now > check_out_dt else "Reserved"

            total_cost = f"₱{row[8]:.2f}" if row[8] else "₱0.00"

            row_data = [
                str(row[0]), row[1], row[2], row[3], row[4], row[6], row[5],
                row[7], total_cost, current_status
            ]

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, item in enumerate(row_data):
                self.table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def early_checkin_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a reserved booking.")
            return

        booking_id = int(self.table.item(selected, 0).text())

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, checkin_time, checkout_date, checkout_time, room_no 
            FROM bookings WHERE id = ?
        """, (booking_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            QMessageBox.warning(self, "Error", "Booking not found.")
            return

        date, old_checkin_time, checkout_date, checkout_time, room_no = result

        now = datetime.now()
        new_checkin_date = now.strftime("%Y-%m-%d")
        new_checkin_time = now.strftime("%H:%M")

        new_checkin_dt = now
        new_checkout_dt = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y-%m-%d %H:%M")

        if new_checkout_dt <= new_checkin_dt:
            QMessageBox.critical(self, "Invalid", "Checkout time must be after the new check-in time.")
            return

        # Conflict check 
        if check_booking_conflict(room_no, new_checkin_dt, new_checkout_dt, booking_id_to_ignore=booking_id):
            QMessageBox.warning(self, "Conflict Detected", "Early check-in conflicts with another booking.")
            return

        # Recalculate total cost
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
        base_price = cursor.fetchone()[0]

        duration_hours = (new_checkout_dt - new_checkin_dt).total_seconds() / 3600
        if duration_hours <= 3:
            total_cost = base_price
        else:
            extra_hours = duration_hours - 3
            total_cost = base_price + (extra_hours * (base_price / 3))

        # Update booking to "checked in"
        cursor.execute("""
            UPDATE bookings
            SET date = ?, checkin_time = ?, status = 'checked in', total_cost = ?
            WHERE id = ?
        """, (new_checkin_date, new_checkin_time, total_cost, booking_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Early Check-In Success", f"Booking is now checked-in. New Total: ₱{int(total_cost)}")
        self.load_data()

    def extend_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a reserved booking to extend.")
            return

        booking_id = int(self.table.item(selected, 0).text())
        current_date = self.table.item(selected, 6).text()  
        current_time = self.table.item(selected, 5).text()  

        dialog = QDialog(self)
        dialog.setWindowTitle("Extend Booking")
        dialog_layout = QVBoxLayout(dialog)

        date_edit = QDateEdit(QDate.fromString(current_date, "yyyy-MM-dd"))
        date_edit.setCalendarPopup(True)
        time_edit = QTimeEdit(QTime.fromString(current_time, "HH:mm"))

        dialog_layout.addWidget(QLabel("New Check-Out Date:"))
        dialog_layout.addWidget(date_edit)
        dialog_layout.addWidget(QLabel("New Check-Out Time:"))
        dialog_layout.addWidget(time_edit)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_new_time(dialog, booking_id, date_edit.date(), time_edit.time()))
        dialog_layout.addWidget(save_btn)

        dialog.exec_()

    def save_new_time(self, dialog, booking_id, new_date, new_time):
        new_date_str = new_date.toString("yyyy-MM-dd")
        new_time_str = new_time.toString("HH:mm")

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT checkin_time, date, room_no FROM bookings WHERE id = ?", (booking_id,))
        checkin_time, checkin_date, room_no = cursor.fetchone()

        checkin_dt = datetime.strptime(f"{checkin_date} {checkin_time}", "%Y-%m-%d %H:%M")
        new_checkout_dt = datetime.strptime(f"{new_date_str} {new_time_str}", "%Y-%m-%d %H:%M")

        if new_checkout_dt <= checkin_dt:
            QMessageBox.critical(self, "Invalid", "New checkout must be after check-in.")
            conn.close()
            return

        if check_booking_conflict(room_no, checkin_dt, new_checkout_dt):
            QMessageBox.warning(self, "Conflict Detected", "Extension conflicts with another booking.")
            conn.close()
            return

        cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
        base_price = cursor.fetchone()[0]

        duration_hours = (new_checkout_dt - checkin_dt).total_seconds() / 3600
        total_cost = base_price if duration_hours <= 3 else base_price + ((duration_hours - 3) * (base_price / 3))

        cursor.execute("""
            UPDATE bookings SET checkout_date = ?, checkout_time = ?, total_cost = ?
            WHERE id = ?
        """, (new_date_str, new_time_str, total_cost, booking_id))
        conn.commit()
        conn.close()

        dialog.accept()
        self.load_data()
        QMessageBox.information(self, "Success", f"Booking extended. New total: ₱{int(total_cost)}")

    def checkout_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a reserved booking to check out.")
            return

        booking_id = int(self.table.item(selected, 0).text())

        confirm = QMessageBox.question(self, "Confirm Check-Out", "Are you sure you want to check out this booking?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'checked out' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        self.load_data()
        QMessageBox.information(self, "Checked Out", "The booking has been checked out successfully.")
