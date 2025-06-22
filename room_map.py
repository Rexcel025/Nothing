from PyQt5.QtWidgets import QWidget, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt
from room_map_ui import Ui_RoomMapWidget
from database import get_room_statuses_for_date, connect_db

status_colors = {
    "vacant": "background-color: #2ecc71;",
    "occupied": "background-color: #e74c3c;",
    "reserved": "background-color: #f1c40f;",
}

class RoomMap(QWidget):
    def __init__(self, parent=None, date=None, on_room_click=None):
        super().__init__(parent)
        self.date = date
        self.on_room_click = on_room_click

        self.ui = Ui_RoomMapWidget()
        self.ui.setupUi(self)

        # Reduce space and margins to make the UI tighter and better
        self.ui.gridLayout.setSpacing(2)
        self.ui.gridLayout.setContentsMargins(5, 5, 5, 5)


        self.ui.titleLabel.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            margin-bottom: 2px;
        """)
        self.refresh_map()

    def refresh_map(self):
        # Set the title label
        self.ui.titleLabel.setText(f"Room Map - {self.date}")

        # Fetch room statuses and prices
        statuses, rooms = get_room_statuses_for_date(self.date)
        prices = self.get_room_prices()
        print("Statuses:", statuses)  #just for debugging hehe
        print("Rooms:", rooms)        
        print("Prices:", prices)     
        # Clear existing buttons in the grid layout
        while self.ui.gridLayout.count():
            child = self.ui.gridLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Dynamically create room buttons
        for idx, room_no in enumerate(rooms):
            status = statuses.get(room_no, "vacant")
            price = prices.get(room_no, "N/A")

            btn = QPushButton(f"Room {room_no}\n{status.capitalize()}\n₱{price}")
            btn.setStyleSheet(f"""
                {status_colors.get(status, 'background-color: #bdc3c7;')}
                border: 1px solid black;
                border-radius: 6px;
                padding: 3px;
                font-size: 9pt;
            """)
            btn.setFixedSize(90, 50) 
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, rn=room_no: self.on_room_click(self.date, rn))


            self.ui.gridLayout.addWidget(btn, idx // 4, idx % 4)  

    def get_room_prices(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT room_no, base_price FROM room_prices")
        prices = {str(room): price for room, price in cursor.fetchall()}
        conn.close()
        return prices
