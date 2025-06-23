from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
import sys
from room_update import RoomUpdate
from calendar_view import CalendarView
from records import RecordsTab
from checked_in_tab import CheckedInTab
from product_management import ProductManagement
from room_management import RoomManagement  # import the new class
from room_map import RoomMap
from register import RegisterWidget
from reserved_tab import ReservedTab

class Dashboard(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Apolonia Hotel System Dashboard")
        self.setGeometry(100, 100, 1000, 600)

        self.role = role
        self.selected_date = None

        # Main container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = QVBoxLayout()
        self.sidebar.setAlignment(Qt.AlignTop)
        main_layout.addLayout(self.sidebar, 1)  # 1 = sidebar width weight

        # Main Area
        self.main_area = QVBoxLayout()
        main_layout.addLayout(self.main_area, 4)  # 4 = main area width weight

        # Add sidebar buttons
        self.add_sidebar_button("Calendar", self.show_calendar)
        self.add_sidebar_button("Records", self.show_records)
        self.add_sidebar_button("Checked-In Customers", self.show_checked_in)
        self.add_sidebar_button("Reserved Customers", self.show_reserved) 
        if self.role == "admin":
            self.add_sidebar_button("Register New User", self.show_register)
            self.add_sidebar_button("Product Management", self.show_product_management)
            self.add_sidebar_button("Room Management", self.show_rooms)

        # Logout Button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.close)
        self.sidebar.addWidget(logout_btn)

        # Default view
        self.show_placeholder("Welcome to Apolonia Hotel System!")

        # Apply Dark Mode to the entire Dashboard
        self.apply_dark_mode()

    def apply_dark_mode(self):
        dark_stylesheet = """
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #5c5c5c;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #505354;
            }
            QPushButton:pressed {
                background-color: #282828;
            }
            QLabel {
                color: #f0f0f0;
            }
            /* Calendar Widget */
            QCalendarWidget QWidget {
                alternate-background-color: #3c3f41;
                background-color: #2b2b2b;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #f0f0f0;
                background-color: #2b2b2b;
                selection-background-color: #505354;
                selection-color: #ffffff;
            }
            QCalendarWidget QToolButton {
                background-color: #3c3f41;
                color: #f0f0f0;
                border: none;
                margin: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #505354;
            }
            QCalendarWidget QSpinBox {
                background-color: #3c3f41;
                color: #f0f0f0;
                border: none;
            }
            /* Table Header */
            QHeaderView::section {
                background-color: #3c3f41;
                color: #f0f0f0;
                padding: 4px;
                border: 1px solid #5c5c5c;
            }
        """
        self.setStyleSheet(dark_stylesheet)


    def add_sidebar_button(self, text, function):
        btn = QPushButton(text)
        btn.clicked.connect(function)
        self.sidebar.addWidget(btn)

    def clear_main_area(self):
        for i in reversed(range(self.main_area.count())):
            widget_to_remove = self.main_area.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

    def show_placeholder(self, text):
        self.clear_main_area()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        self.main_area.addWidget(label)

    def show_calendar(self):
        self.clear_main_area()
        self.calendar_widget = CalendarView(self.on_day_selected)
        self.main_area.addWidget(self.calendar_widget)

    def on_day_selected(self, year, month, day):
        selected_date = f"{year}-{month:02d}-{day:02d}"
        print("Selected Date:", selected_date)
        self.selected_date = selected_date
        self.show_room_map_for_date(selected_date)

    def show_room_map_for_date(self, date):
        print("Room Map Date:", date)
        room_map_widget = RoomMap(parent=None, date=date, on_room_click=self.on_room_click)
        self.clear_main_area()
        self.main_area.addWidget(room_map_widget)



    def on_room_click(self, date, room_no):
        print(f"Clicked Room {room_no} on {date}")
        self.room_update_window = RoomUpdate(date, room_no, refresh_callback=lambda: self.show_room_map_for_date(date))
        self.room_update_window.show()


    def show_records(self):
        self.clear_main_area()
        records_widget = RecordsTab(self.role)
        self.main_area.addWidget(records_widget)

    def show_checked_in(self):
        self.clear_main_area()
        checked_in_widget = CheckedInTab()
        self.main_area.addWidget(checked_in_widget)

    def show_register(self):
        self.clear_main_area()
        register_widget = RegisterWidget()
        self.main_area.addWidget(register_widget)



    def show_product_management(self):
        self.clear_main_area()
        product_widget = ProductManagement()
        self.main_area.addWidget(product_widget)


    def show_rooms(self):
        self.clear_main_area()
        room_widget = RoomManagement()  # instantiate the widget class
        self.main_area.addWidget(room_widget)
        
    def show_reserved(self):
        self.clear_main_area()  # Clear the main area like other pages
        reserved_widget = ReservedTab()  # Create ReservedTab instance
        self.main_area.addWidget(reserved_widget)  # Show in the main area


def open_dashboard(role):
    app = QApplication(sys.argv)
    window = Dashboard(role)
    window.show()
    sys.exit(app.exec_())
