# calendar_view.py

import tkinter as tk
import calendar
from datetime import datetime

def show_calendar(main_area, on_day_selected):
    # Clear the main area
    for widget in main_area.winfo_children():
        widget.destroy()

    # Get current date info
    now = datetime.now()
    year = now.year
    month = now.month
    month_name = calendar.month_name[month]

    # Header
    header = tk.Label(main_area, text=f"{month_name} {year}", font=("Arial", 18))
    header.pack(pady=10)

    # Calendar grid frame
    calendar_frame = tk.Frame(main_area)
    calendar_frame.pack()

    # Day headers
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        tk.Label(calendar_frame, text=day, font=("Arial", 12, "bold"), width=10).grid(row=0, column=i)

    # Calendar days
    cal = calendar.Calendar(firstweekday=0)
    row = 1
    for week in cal.monthdayscalendar(year, month):
        for col, day in enumerate(week):
            if day == 0:
                continue
            btn = tk.Button(
                calendar_frame,
                text=str(day),
                width=10,
                height=2,
                command=lambda d=day: on_day_selected(year, month, d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
        row += 1
