from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import QDate, Qt
from calendar_ui import Ui_CalendarViewWidget

class CalendarView(QWidget):
    def __init__(self, on_day_selected_callback):
        super().__init__()
        self.ui = Ui_CalendarViewWidget()
        self.ui.setupUi(self)

        self.on_day_selected_callback = on_day_selected_callback

        # Connect calendar click to callback
        self.ui.calendarWidget.clicked.connect(self.handle_date_selected)

        # Calendar appearance settings for dark mode

        self.ui.calendarWidget.setGridVisible(True)
        self.ui.calendarWidget.setVerticalHeaderFormat(self.ui.calendarWidget.NoVerticalHeader)
        self.ui.calendarWidget.setHorizontalHeaderFormat(self.ui.calendarWidget.SingleLetterDayNames)
        self.ui.calendarWidget.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                selection-background-color: #555;
                background-color: #2b2b2b;
                color: #f0f0f0;  /* Normal day number text color */
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #333; 
                color: #f0f0f0; 
            }
            QCalendarWidget QToolButton {
                color: #f0f0f0;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #f0f0f0; /* prevents weekend red text */
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #2b2b2b; /* hidden overflow days */
            }
        """)


        self.hide_overflow_days()

        # when navigating to another month, refresh hidden overflow days
        self.ui.calendarWidget.currentPageChanged.connect(lambda: self.hide_overflow_days())

    def handle_date_selected(self, qdate: QDate):
        year = qdate.year()
        month = qdate.month()
        day = qdate.day()
        print(f"Date clicked: {year}-{month:02d}-{day:02d}")
        self.on_day_selected_callback(year, month, day)

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
                            view.setIndexWidget(index, QLabel(""))  # Replaces overflow day with empty label
