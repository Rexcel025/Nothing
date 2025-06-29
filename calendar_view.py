from PyQt5.QtWidgets import QWidget, QLabel, QToolTip, QVBoxLayout, QCalendarWidget, QTableView
from PyQt5.QtCore import QDate, Qt
from calendar_ui import Ui_CalendarViewWidget
from database import connect_db
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QCalendarWidget, QTableView, QLabel
from PyQt5.QtCore import Qt, QTimer, QDate

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, get_booked_reserved_count_func, parent=None):
        super().__init__(parent)
        self.get_booked_reserved_count_func = get_booked_reserved_count_func
        self._table_view = None
        QTimer.singleShot(0, self.init_table_view)
        self._floating_label = None  # Store reference

    def init_table_view(self):
        self._table_view = self.findChild(QTableView)

    def contextMenuEvent(self, event):
        qdate = None
        if self._table_view:
            table_pos = self._table_view.viewport().mapFromGlobal(self.mapToGlobal(event.pos()))
            index = self._table_view.indexAt(table_pos)
            if index.isValid():
                day = index.data(0)
                if isinstance(day, int):
                    year = self.yearShown()
                    month = self.monthShown()
                    try:
                        qdate = QDate(year, month, day)
                    except Exception as e:
                        print(f"Could not create QDate from {year}-{month}-{day}: {e}")
        if not qdate or not qdate.isValid():
            qdate = self.selectedDate()
        count = self.get_booked_reserved_count_func(qdate)
        msg = f"Customers on {qdate.toString('yyyy-MM-dd')}: {count}"

        # Destroy old label if present
        if self._floating_label is not None:
            self._floating_label.close()
            self._floating_label = None

        # Create floating label
        self._floating_label = QLabel(msg, self)
        self._floating_label.setStyleSheet("""
            background: #222; color: #fff;
            border: 1px solid #888;
            padding: 6px 14px;
            border-radius: 7px;
        """)
        self._floating_label.setWindowFlags(Qt.ToolTip)
        self._floating_label.adjustSize()
        self._floating_label.move(self.mapFromGlobal(event.globalPos()))
        self._floating_label.show()

        # Auto-hide after 2.5 seconds (or adjust as you like)
        QTimer.singleShot(2500, self._floating_label.close)


class CalendarView(QWidget):
    def __init__(self, on_day_selected_callback):
        super().__init__()
        self.ui = Ui_CalendarViewWidget()
        self.ui.setupUi(self)
        self.on_day_selected_callback = on_day_selected_callback

        # Replace the default QCalendarWidget with the custom one
        old_calendar = self.ui.calendarWidget
        layout = self.layout() or QVBoxLayout(self)
        layout.removeWidget(old_calendar)
        old_calendar.deleteLater()

        self.ui.calendarWidget = CustomCalendarWidget(self.get_booked_reserved_count, self)
        layout.insertWidget(0, self.ui.calendarWidget)

        self.ui.calendarWidget.clicked.connect(self.handle_date_selected)
        self.ui.calendarWidget.setGridVisible(True)
        self.ui.calendarWidget.setVerticalHeaderFormat(self.ui.calendarWidget.NoVerticalHeader)
        self.ui.calendarWidget.setHorizontalHeaderFormat(self.ui.calendarWidget.SingleLetterDayNames)


        self.hide_overflow_days()
        self.ui.calendarWidget.currentPageChanged.connect(lambda: self.hide_overflow_days())

    def handle_date_selected(self, qdate: QDate):
        year = qdate.year()
        month = qdate.month()
        day = qdate.day()
        print(f"Date clicked: {year}-{month:02d}-{day:02d}")
        self.on_day_selected_callback(year, month, day)

    def get_booked_reserved_count(self, qdate: QDate):
        selected_date = qdate.toString("yyyy-MM-dd")
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT room_no) FROM bookings
            WHERE date <= ? AND checkout_date >= ?
            AND status IN ('reserved', 'checked in')
            """,
            (selected_date, selected_date)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def hide_overflow_days(self):
        view = self.ui.calendarWidget.findChild(QWidget, "qt_calendar_calendarview")
        if view:
            model = view.model()
            this_month = self.ui.calendarWidget.monthShown()
            for row in range(model.rowCount()):
                for col in range(model.columnCount()):
                    index = model.index(row, col)
                    date = index.data(0)
                    if isinstance(date, QDate):
                        if date.month() != this_month:
                            view.setIndexWidget(index, QLabel(""))  
