import tkinter as tk
import calendar
from datetime import datetime

def show_calendar(main_area, on_day_selected):
    # Clear the main area
    for widget in main_area.winfo_children():
        widget.destroy()

    # State to hold the currently displayed month/year
    state = {"year": datetime.now().year, "month": datetime.now().month}

    def refresh_calendar():
        # Clear calendar frame only
        for widget in calendar_frame.winfo_children():
            widget.destroy()

        year = state["year"]
        month = state["month"]
        month_name = calendar.month_name[month]
        header.config(text=f"{month_name} {year}")

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

    def go_prev():
        if state["month"] == 1:
            state["month"] = 12
            state["year"] -= 1
        else:
            state["month"] -= 1
        refresh_calendar()

    def go_next():
        if state["month"] == 12:
            state["month"] = 1
            state["year"] += 1
        else:
            state["month"] += 1
        refresh_calendar()

    # Header with month/year
    header_frame = tk.Frame(main_area)
    header_frame.pack(pady=10)

    prev_btn = tk.Button(header_frame, text="<< Prev", command=go_prev)
    prev_btn.pack(side="left", padx=5)

    header = tk.Label(header_frame, text="", font=("Arial", 18))
    header.pack(side="left", padx=10)

    next_btn = tk.Button(header_frame, text="Next >>", command=go_next)
    next_btn.pack(side="left", padx=5)

    # Calendar grid frame
    calendar_frame = tk.Frame(main_area)
    calendar_frame.pack()

    # Initial render
    refresh_calendar()
