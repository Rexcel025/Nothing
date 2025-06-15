from calendar_view import show_calendar
from room_map import show_room_map
from room_update import show_room_update
from records import show_records_screen
from checked_in_tab import show_checked_in_tab

import tkinter as tk
from tkinter import messagebox

def open_dashboard(role):
    dashboard = tk.Tk()
    dashboard.title("Hotel System Dashboard")

    # Sidebar Frame
    sidebar = tk.Frame(dashboard, bg="#2c3e50", width=200, height=500)
    sidebar.pack(side="left", fill="y")

    main_area = tk.Frame(dashboard, bg="#ecf0f1", width=600, height=500)
    main_area.pack(side="right", expand=True, fill="both")

    selected_date = None  # Will store last selected date

    def show_placeholder(text):
        for widget in main_area.winfo_children():
            widget.destroy()
        tk.Label(main_area, text=text, font=("Arial", 16)).pack(pady=20)

    def refresh_room_map():
        if selected_date:
            show_room_map(main_area, selected_date, on_room_click)

    def on_day_selected(year, month, day):
        nonlocal selected_date
        selected_date = f"{year}-{month:02d}-{day:02d}"
        show_room_map(main_area, selected_date, on_room_click)

    def on_room_click(selected_date, room_no, refresh_map):
        show_room_update(main_area, selected_date, room_no, refresh_map)


    # Sidebar buttons
    def add_sidebar_button(text, command):
        tk.Button(sidebar, text=text, width=25, pady=5, command=command).pack(pady=5)

    add_sidebar_button("Calendar", lambda: show_calendar(main_area, on_day_selected))
    add_sidebar_button("Records", lambda: show_records_screen(main_area, role))
    add_sidebar_button("Checked-In Customers", lambda: show_checked_in_tab(main_area))

    if role == "admin":
        add_sidebar_button("Register New User", lambda: show_placeholder("User Registration"))

    tk.Button(sidebar, text="Logout", fg="red", command=dashboard.destroy).pack(side="bottom", pady=10)

    dashboard.mainloop()
