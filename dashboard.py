from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from room_update import RoomUpdate
from calendar_view import CalendarView
from records import RecordsTab
from checked_in_tab import CheckedInTab
from product_management import ProductManagement
from room_management import RoomManagement
from room_map import RoomMap
from register import RegisterWidget
from reserved_tab import ReservedTab


from login import LoginWindow  

class Dashboard(QMainWindow):
    def __init__(self, role, login_window_class=LoginWindow):
        super().__init__()
        self.setWindowTitle("Apolonia Hotel System Dashboard")
        self.setGeometry(100, 100, 1100, 700)
        self.role = role
        self.selected_date = None
        self.login_window_class = login_window_class  

        # Main container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(sidebar, 0)

        # Sidebar Buttons
        self.sidebar_buttons = []
        self.sidebar_btn_data = [
            ("Calendar", self.show_calendar),
            ("Records", self.show_records),
            ("Checked-In Customers", self.show_checked_in),
            ("Reserved Customers", self.show_reserved)
        ]
        if self.role == "admin":
            self.sidebar_btn_data += [
                ("Register New User", self.show_register),
                ("Product Management", self.show_product_management),
                ("Room Management", self.show_rooms)
            ]

        self.sidebar_btn_data.append(("Logout", self.logout_action))

        for text, func in self.sidebar_btn_data:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        # Main Content Area 
        self.card_widget = QWidget()
        self.card_widget.setObjectName("Card")
        self.card_layout = QVBoxLayout(self.card_widget)
        self.card_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.card_widget, 1)

        # Title at the top of the content area
        self.main_title = QLabel("Apolonia Hotel System Dashboard")
        self.main_title.setObjectName("MainTitle")
        self.card_layout.addWidget(self.main_title)

        # Placeholder for the first view
        self.show_placeholder("Welcome to Apolonia Hotel System!")

    def set_main_title(self, text):
        self.main_title.setText(text)

    def clear_card(self):
        # Remove all widgets in card except title
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(1)
            if item.widget():
                item.widget().setParent(None)

    def show_placeholder(self, text):
        self.clear_card()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(label)

    def show_calendar(self):
        self.clear_card()
        self.set_main_title("Calendar")
        calendar_widget = CalendarView(self.on_day_selected)
        self.card_layout.addWidget(calendar_widget)

    def on_day_selected(self, year, month, day):
        selected_date = f"{year}-{month:02d}-{day:02d}"
        print("Selected Date:", selected_date)
        self.selected_date = selected_date
        self.show_room_map_for_date(selected_date)

    def show_room_map_for_date(self, date):
        self.clear_card()
        self.set_main_title(f"Room Map: {date}")
        room_map_widget = RoomMap(parent=None, date=date, on_room_click=self.on_room_click)
        self.card_layout.addWidget(room_map_widget)

    def on_room_click(self, date, room_no):
        self.room_update_window = RoomUpdate(date, room_no, refresh_callback=lambda: self.show_room_map_for_date(date))
        self.room_update_window.show()

    def show_records(self):
        self.clear_card()
        self.set_main_title("Booking Records")
        records_widget = RecordsTab(self.role)
        self.card_layout.addWidget(records_widget)

    def show_checked_in(self):
        self.clear_card()
        self.set_main_title("Checked-In Customers")
        checked_in_widget = CheckedInTab()
        self.card_layout.addWidget(checked_in_widget)

    def show_register(self):
        self.clear_card()
        self.set_main_title("Register New User")
        register_widget = RegisterWidget()
        self.card_layout.addWidget(register_widget)

    def show_product_management(self):
        self.clear_card()
        self.set_main_title("Product Management")
        product_widget = ProductManagement()
        self.card_layout.addWidget(product_widget)

    def show_rooms(self):
        self.clear_card()
        self.set_main_title("Room Management")
        room_widget = RoomManagement()
        self.card_layout.addWidget(room_widget)

    def show_reserved(self):
        self.clear_card()
        self.set_main_title("Reserved Customers")
        reserved_widget = ReservedTab()
        self.card_layout.addWidget(reserved_widget)


    def logout_action(self):
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
