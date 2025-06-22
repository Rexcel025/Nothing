from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QDateEdit, QTimeEdit
from PyQt5.QtCore import Qt, QDate, QTime
from datetime import datetime
from database import connect_db, check_booking_conflict 

class CheckedInTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        title = QLabel("Checked-In Customers")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Room", "Name", "Check-In", "Check-Out Time", "Check-Out Date", "Status", "Total Cost", "Current Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        extend_btn = QPushButton("Extend Booking")
        extend_btn.clicked.connect(self.extend_selected)
        checkout_btn = QPushButton("Check Out")
        checkout_btn.clicked.connect(self.checkout_selected)
        button_layout.addWidget(extend_btn)
        button_layout.addWidget(checkout_btn)
        self.layout.addLayout(button_layout)

        self.load_data()

    def load_data(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE status = 'checked in'")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        now = datetime.now()

        for row in rows:
            try:
                # Correct order: checkout_date first, then checkout_time
                check_in_dt = datetime.strptime(f"{row[1]} {row[4]}", "%Y-%m-%d %H:%M")
                check_out_dt = datetime.strptime(f"{row[5]} {row[6]}", "%Y-%m-%d %H:%M")
                current_status = "Overstayed" if now > check_out_dt else "Checked In"
            except Exception as e:
                current_status = f"Error: {e}"

            total_cost = f"₱{row[8]:.2f}" if row[8] else "₱0.00"

            # Note: Using correct order for checkout_date and checkout_time in display as well
            row_data = [
                str(row[0]),  # ID
                row[1],       # Date
                row[2],       # Room
                row[3],       # Name
                row[4],       # Check-In Time
                row[6],       # Check-Out Time
                row[5],       # Check-Out Date
                row[7],       # Status
                total_cost,   # Total Cost
                current_status  # Current Status
            ]

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, item in enumerate(row_data):
                self.table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def extend_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a booking to extend.")
            return

        booking_id = self.table.item(selected, 0).text()
        current_date = self.table.item(selected, 6).text()  # Check-Out Date
        current_time = self.table.item(selected, 5).text()  # Check-Out Time

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

        check_in_dt = datetime.strptime(f"{checkin_date} {checkin_time}", "%Y-%m-%d %H:%M")
        check_out_dt = datetime.strptime(f"{new_date_str} {new_time_str}", "%Y-%m-%d %H:%M")

        if check_out_dt <= check_in_dt:
            QMessageBox.critical(self, "Invalid", "New checkout must be after check-in.")
            conn.close()
            return

        # 🛡️ Check for conflict here:
        from database import check_booking_conflict  # Important: make sure this is imported at the top
        conflict = check_booking_conflict(room_no, check_in_dt, check_out_dt, exclude_booking_id=booking_id)
        if conflict:
            QMessageBox.critical(self, "Conflict", "Extension overlaps with another booking.")
            conn.close()
            return

        cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
        base_price = cursor.fetchone()[0]

        duration_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
        if duration_hours <= 3:
            total_cost = base_price
        else:
            extra_hours = duration_hours - 3
            total_cost = base_price + (extra_hours * (base_price / 3))

        cursor.execute("""
            UPDATE bookings SET checkout_time = ?, checkout_date = ?, total_cost = ?
            WHERE id = ?
        """, (new_time_str, new_date_str, total_cost, booking_id))
        conn.commit()
        conn.close()

        dialog.accept()
        self.load_data()
        QMessageBox.information(self, "Success", f"Booking extended. New total cost: ₱{int(total_cost)}")
    def checkout_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a booking to check out.")
            return

        booking_id = self.table.item(selected, 0).text()

        confirm = QMessageBox.question(self, "Confirm Check-Out", "Are you sure you want to check out this booking?",
                                    QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        conn = connect_db()
        cursor = conn.cursor()
        # Correct status here
        cursor.execute("UPDATE bookings SET status = 'checked out' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        self.load_data()
        QMessageBox.information(self, "Checked Out", "The booking has been checked out successfully.")
