from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QDateEdit,
    QLineEdit, QMessageBox
)
from PyQt5.QtCore import QDate
from database import save_booking_with_cost, connect_db
from datetime import datetime

class RoomUpdate(QWidget):
    def __init__(self, date, room_no, refresh_callback=None):
        super().__init__()
        self.date = date
        self.room_no = room_no
        self.refresh_callback = refresh_callback

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = QLabel(f"Room Update - Room {self.room_no} on {self.date}")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f0f0f0;")
        layout.addWidget(title)

        form_layout = QVBoxLayout()

        # Customer Name
        self.name_input = QLineEdit()
        form_layout.addWidget(QLabel("Customer Name:"))
        form_layout.addWidget(self.name_input)

        # Check-in Time
        form_layout.addWidget(QLabel("Check-in Time:"))
        checkin_layout = QHBoxLayout()
        self.checkin_hour = QComboBox()
        self.checkin_hour.addItems([f"{h:02d}" for h in range(24)])
        self.checkin_hour.setCurrentText("12")
        self.checkin_minute = QComboBox()
        self.checkin_minute.addItems([f"{m:02d}" for m in range(0, 60, 5)])
        checkin_layout.addWidget(self.checkin_hour)
        checkin_layout.addWidget(QLabel(":"))
        checkin_layout.addWidget(self.checkin_minute)
        form_layout.addLayout(checkin_layout)

        # Check-out Time
        form_layout.addWidget(QLabel("Check-out Time:"))
        checkout_layout = QHBoxLayout()
        self.checkout_hour = QComboBox()
        self.checkout_hour.addItems([f"{h:02d}" for h in range(24)])
        self.checkout_hour.setCurrentText("14")
        self.checkout_minute = QComboBox()
        self.checkout_minute.addItems([f"{m:02d}" for m in range(0, 60, 5)])
        checkout_layout.addWidget(self.checkout_hour)
        checkout_layout.addWidget(QLabel(":"))
        checkout_layout.addWidget(self.checkout_minute)
        form_layout.addLayout(checkout_layout)

        # Check-out Date
        form_layout.addWidget(QLabel("Check-out Date:"))
        self.checkout_date = QDateEdit()
        self.checkout_date.setDate(QDate.fromString(self.date, "yyyy-MM-dd"))
        self.checkout_date.setCalendarPopup(True)
        form_layout.addWidget(self.checkout_date)

        # Status
        form_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["checked in", "reserved"])
        form_layout.addWidget(self.status_combo)

        # Save Button
        save_button = QPushButton("Save Booking")
        save_button.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 4px;")
        save_button.clicked.connect(self.save_data)

        layout.addLayout(form_layout)
        layout.addWidget(save_button)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

    def save_data(self):
        name = self.name_input.text()
        checkin = f"{self.checkin_hour.currentText()}:{self.checkin_minute.currentText()}"
        checkout = f"{self.checkout_hour.currentText()}:{self.checkout_minute.currentText()}"
        checkout_date = self.checkout_date.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        if not name:
            QMessageBox.critical(self, "Error", "Customer name cannot be empty.")
            return

        checkin_dt = datetime.strptime(f"{self.date} {checkin}", "%Y-%m-%d %H:%M")
        checkout_dt = datetime.strptime(f"{checkout_date} {checkout}", "%Y-%m-%d %H:%M")
        duration_hours = (checkout_dt - checkin_dt).total_seconds() / 3600

        if duration_hours <= 0:
            QMessageBox.critical(self, "Error", "Check-out must be after check-in.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (self.room_no,))
        result = cursor.fetchone()
        conn.close()
        base_price = result[0] if result else 0

        if duration_hours <= 3:
            total_cost = base_price
        else:
            extra_hours = duration_hours - 3
            total_cost = base_price + (extra_hours * (base_price / 3))

        # NEW: Handle booking conflict here
        success = save_booking_with_cost(
            self.date, self.room_no, name, checkin, checkout_date, checkout, status, total_cost
        )

        if not success:
            QMessageBox.warning(self, "Booking Conflict", "Cannot save booking: room is already booked during this period.")
            return

        QMessageBox.information(self, "Success", f"Booking saved! Total Cost: ₱{int(total_cost)}")

        if self.refresh_callback:
            self.refresh_callback()
