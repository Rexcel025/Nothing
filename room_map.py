from PyQt5.QtWidgets import QWidget, QPushButton, QSizePolicy, QLabel
from PyQt5.QtCore import Qt, QTimer
from room_map_ui import Ui_RoomMapWidget
from database import get_room_statuses_for_date, connect_db, get_bookings_for_room_and_date

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
        self.ui.gridLayout.setSpacing(2)
        self.ui.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.ui.titleLabel.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            margin-bottom: 2px;
        """)
        self._floating_label = None 
        self.refresh_map()

    def refresh_map(self):
        self.ui.titleLabel.setText(f"Room Map - {self.date}")
        statuses, rooms = get_room_statuses_for_date(self.date)
        prices = self.get_room_prices()

        # Clear old buttons
        while self.ui.gridLayout.count():
            child = self.ui.gridLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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
            btn.setFixedSize(195, 120)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # Standard left click behavior
            btn.clicked.connect(lambda _, rn=room_no: self.on_room_click(self.date, rn))

            # Right-click sticky tooltip
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, rn=room_no, b=btn: self.show_room_tooltip(rn, b, pos)
            )

            self.ui.gridLayout.addWidget(btn, idx // 4, idx % 4)

    def get_room_prices(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT room_no, base_price FROM room_prices")
        prices = {str(room): price for room, price in cursor.fetchall()}
        conn.close()
        return prices

    def show_room_tooltip(self, room_no, button, pos):
        # Destroy old label if present
        if hasattr(self, "_floating_label") and self._floating_label is not None:
            self._floating_label.close()
            self._floating_label = None

        bookings = get_bookings_for_room_and_date(room_no, self.date)
        if not bookings:
            msg = "No bookings for this room."
        else:
            msg_lines = []
            for customer, out_date, out_time, status in bookings:
                # Format MM-DD from out_date string (yyyy-mm-dd)
                mmdd = out_date[5:] if len(out_date) == 10 else out_date
                tag = "(C)" if status.lower().startswith("checked in") else "(R)"
                msg_lines.append(f"{customer}  {mmdd} {out_time} {tag}")
            msg = "\n".join(msg_lines)

        self._floating_label = QLabel(msg, self)
        self._floating_label.setStyleSheet("""
            background: #222; color: #fff;
            border: 1px solid #888;
            padding: 6px 14px;
            border-radius: 7px;
            font-family: 'Consolas', 'monospace';
        """)
        self._floating_label.setWindowFlags(Qt.ToolTip)
        self._floating_label.adjustSize()

        # Popup near mouse position relative to button
        global_pos = button.mapToGlobal(pos)
        widget_pos = self.mapFromGlobal(global_pos)
        self._floating_label.move(widget_pos)
        self._floating_label.show()
        QTimer.singleShot(2500, self._floating_label.close)
