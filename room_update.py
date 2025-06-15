import tkinter as tk
from tkinter import ttk, messagebox
from database import save_booking, connect_db

def show_room_update(main_area, date, room_no, refresh_callback):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text=f"Room Update - Room {room_no} on {date}", font=("Arial", 16)).pack(pady=10)

    form_frame = tk.Frame(main_area)
    form_frame.pack(pady=10)

    # Customer Name
    tk.Label(form_frame, text="Customer Name:").grid(row=0, column=0, sticky="e")
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, pady=5)

    # Check-in Time (Dropdowns)
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

    # Check-out Time (Dropdowns)
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

    # Status
    tk.Label(form_frame, text="Status:").grid(row=3, column=0, sticky="e")
    status_var = tk.StringVar(value="occupied")
    status_menu = ttk.Combobox(form_frame, textvariable=status_var, values=["occupied", "reserved"])
    status_menu.grid(row=3, column=1, pady=5)

    # Save Booking
    def save_data():
        name = name_entry.get()
        checkin = f"{checkin_hour.get()}:{checkin_minute.get()}"
        checkout = f"{checkout_hour.get()}:{checkout_minute.get()}"
        status = status_var.get()

        if not name or not checkin or not checkout:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        save_booking(date, room_no, name, checkin, checkout, status)
        messagebox.showinfo("Success", "Booking saved to database!")
        refresh_callback()

    # Clear Room
    def clear_room():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings SET status = 'vacant'
            WHERE room_no = ? AND date = ?
        """, (room_no, date))
        conn.commit()
        conn.close()
        messagebox.showinfo("Cleared", f"Room {room_no} marked as vacant.")
        refresh_callback()

    # Buttons
    btn_frame = tk.Frame(main_area)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Save Booking", command=save_data, bg="#3498db", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Clear Room", command=clear_room, bg="#e67e22", fg="white").pack(side="left", padx=10)
