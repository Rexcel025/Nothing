import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import save_booking_with_cost, connect_db
from datetime import datetime, timedelta

def show_room_update(main_area, date, room_no, refresh_callback):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text=f"Room Update - Room {room_no} on {date}", font=("Arial", 16)).pack(pady=10)

    form_frame = tk.Frame(main_area)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Customer Name:").grid(row=0, column=0, sticky="e")
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Check-in Time:").grid(row=1, column=0, sticky="e")
    checkin_frame = tk.Frame(form_frame)
    checkin_frame.grid(row=1, column=1, pady=5)

    checkin_hour = ttk.Combobox(checkin_frame, values=[f"{h:02d}" for h in range(24)], width=3)
    checkin_hour.set("12")
    checkin_hour.pack(side="left")
    tk.Label(checkin_frame, text=":").pack(side="left")
    checkin_minute = ttk.Combobox(checkin_frame, values=[f"{m:02d}" for m in range(0, 60, 5)], width=3)
    checkin_minute.set("00")
    checkin_minute.pack(side="left")

    tk.Label(form_frame, text="Check-out Time:").grid(row=2, column=0, sticky="e")
    checkout_frame = tk.Frame(form_frame)
    checkout_frame.grid(row=2, column=1, pady=5)

    checkout_hour = ttk.Combobox(checkout_frame, values=[f"{h:02d}" for h in range(24)], width=3)
    checkout_hour.set("14")
    checkout_hour.pack(side="left")
    tk.Label(checkout_frame, text=":").pack(side="left")
    checkout_minute = ttk.Combobox(checkout_frame, values=[f"{m:02d}" for m in range(0, 60, 5)], width=3)
    checkout_minute.set("00")
    checkout_minute.pack(side="left")

    tk.Label(form_frame, text="Check-out Date:").grid(row=3, column=0, sticky="e")
    checkout_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    checkout_date_entry.set_date(date)
    checkout_date_entry.grid(row=3, column=1, pady=5)

    tk.Label(form_frame, text="Status:").grid(row=4, column=0, sticky="e")
    status_var = tk.StringVar(value="occupied")
    status_menu = ttk.Combobox(form_frame, textvariable=status_var, values=["occupied", "reserved"])
    status_menu.grid(row=4, column=1, pady=5)

    def save_data():
        name = name_entry.get()
        checkin = f"{checkin_hour.get()}:{checkin_minute.get()}"
        checkout = f"{checkout_hour.get()}:{checkout_minute.get()}"
        checkout_date = checkout_date_entry.get_date().strftime("%Y-%m-%d")
        status = status_var.get()

        if not name or not checkin or not checkout:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        checkin_dt = datetime.strptime(f"{date} {checkin}", "%Y-%m-%d %H:%M")
        checkout_dt = datetime.strptime(f"{checkout_date} {checkout}", "%Y-%m-%d %H:%M")
        duration_hours = (checkout_dt - checkin_dt).total_seconds() / 3600

        if duration_hours <= 0:
            messagebox.showerror("Error", "Check-out must be after check-in.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
        result = cursor.fetchone()
        conn.close()

        base_price = result[0] if result else 0

        if duration_hours <= 3:
            total_cost = base_price
        else:
            extra_hours = duration_hours - 3
            total_cost = base_price + (extra_hours * (base_price / 3))

        save_booking_with_cost(date, room_no, name, checkin, checkout, checkout_date, status, total_cost)
        messagebox.showinfo("Success", f"Booking saved! Total Cost: ₱{int(total_cost)}")

        if refresh_callback:
            refresh_callback()

    tk.Button(main_area, text="Save Booking", command=save_data, bg="#3498db", fg="white").pack(pady=10)
