from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
)
from database import connect_db

class RoomManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_rooms()

    def initUI(self):
        main_layout = QVBoxLayout()

        title = QLabel("Room Management")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Form Layout
        form_layout = QVBoxLayout()

        room_no_layout = QHBoxLayout()
        room_no_label = QLabel("Room No:")
        self.room_no_input = QLineEdit()
        room_no_layout.addWidget(room_no_label)
        room_no_layout.addWidget(self.room_no_input)
        form_layout.addLayout(room_no_layout)

        price_layout = QHBoxLayout()
        price_label = QLabel("Base Price:")
        self.price_input = QLineEdit()
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        form_layout.addLayout(price_layout)

        # Buttons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Add Room")
        add_btn.clicked.connect(self.add_room)
        button_layout.addWidget(add_btn)

        update_btn = QPushButton("Update Price")
        update_btn.clicked.connect(self.update_room)
        button_layout.addWidget(update_btn)

        delete_btn = QPushButton("Remove Room")
        delete_btn.clicked.connect(self.delete_room)
        button_layout.addWidget(delete_btn)

        form_layout.addLayout(button_layout)

        main_layout.addLayout(form_layout)

        # Room List
        self.room_list = QListWidget()
        main_layout.addWidget(QLabel("Existing Rooms:"))
        main_layout.addWidget(self.room_list)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

    def load_rooms(self):
        self.room_list.clear()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT room_no, base_price FROM room_prices")
        for room_no, price in cursor.fetchall():
            self.room_list.addItem(f"Room {room_no}: ₱{price}")
        conn.close()

    def add_room(self):
        room_no = self.room_no_input.text().strip()
        try:
            price = float(self.price_input.text())
            if not room_no:
                raise ValueError("Room No cannot be empty.")
        except ValueError as ve:
            QMessageBox.critical(self, "Invalid Input", str(ve))
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO room_prices (room_no, base_price) VALUES (?, ?)", (room_no, price))
            conn.commit()
            QMessageBox.information(self, "Success", "Room added successfully.")
            self.load_rooms()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        conn.close()

    def update_room(self):
        room_no = self.room_no_input.text().strip()
        try:
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Enter a valid price.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE room_prices SET base_price = ? WHERE room_no = ?", (price, room_no))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Room updated successfully.")
        self.load_rooms()

    def delete_room(self):
        room_no = self.room_no_input.text().strip()
        if not room_no:
            QMessageBox.critical(self, "Invalid Input", "Enter Room No to delete.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM room_prices WHERE room_no = ?", (room_no,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Room deleted successfully.")
        self.load_rooms()
