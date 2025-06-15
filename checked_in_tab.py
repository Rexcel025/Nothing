import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import connect_db

def show_checked_in_tab(main_area):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Checked-In Customers", font=("Arial", 16)).pack(pady=10)

    tree = ttk.Treeview(main_area, columns=(
        "ID", "Date", "Room", "Name", "Check-In", "Check-Out", "Status", "Current Status"), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.pack(expand=True, fill="both", padx=10, pady=5)

    def load_checked_in_data():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE status = 'occupied'")
        rows = cursor.fetchall()
        conn.close()

        tree.delete(*tree.get_children())
        now = datetime.now()

        for row in rows:
            try:
                check_in_dt = datetime.strptime(f"{row[1]} {row[4]}", "%Y-%m-%d %H:%M")
                check_out_dt = datetime.strptime(f"{row[1]} {row[5]}", "%Y-%m-%d %H:%M")

                # If checkout is earlier than check-in, assume it's the next day
                if check_out_dt < check_in_dt:
                    check_out_dt += timedelta(days=1)

                current_status = "Overstayed" if now > check_out_dt else "Checked In"
            except Exception as e:
                current_status = "Invalid Time"

            tree.insert("", "end", values=(*row, current_status))

    def check_out_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a customer to check out.")
            return

        booking_id = tree.item(selected[0])["values"][0]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'vacant' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Customer has been checked out.")
        load_checked_in_data()

    def extend_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a customer to extend.")
            return

        values = tree.item(selected[0])["values"]
        booking_id = values[0]
        current_checkout = values[5]

        # Split current time for default dropdown values
        try:
            hour, minute = current_checkout.split(":")
        except ValueError:
            hour, minute = "12", "00"

        extend_window = tk.Toplevel()
        extend_window.title("Extend Booking")

        tk.Label(extend_window, text="New Check-Out Time:").pack(pady=5)

        time_frame = tk.Frame(extend_window)
        time_frame.pack(pady=5)

        hour_var = tk.StringVar()
        minute_var = tk.StringVar()

        hour_combo = ttk.Combobox(time_frame, textvariable=hour_var, values=[f"{h:02d}" for h in range(24)], width=3)
        hour_combo.set(hour)
        hour_combo.pack(side="left")

        tk.Label(time_frame, text=":").pack(side="left")

        minute_combo = ttk.Combobox(time_frame, textvariable=minute_var, values=[f"{m:02d}" for m in range(0, 60, 5)], width=3)
        minute_combo.set(minute)
        minute_combo.pack(side="left")

        def save_new_time():
            new_hour = hour_var.get()
            new_minute = minute_var.get()

            if not new_hour or not new_minute:
                messagebox.showerror("Invalid", "Please select both hour and minute.")
                return

            new_time = f"{new_hour}:{new_minute}"

            try:
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Invalid", "Enter time in HH:MM format.")
                return

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE bookings SET checkout_time = ? WHERE id = ?", (new_time, booking_id))
            conn.commit()
            conn.close()
            extend_window.destroy()
            load_checked_in_data()
            messagebox.showinfo("Success", "Checkout time updated.")

        tk.Button(extend_window, text="Save", command=save_new_time).pack(pady=10)

    button_frame = tk.Frame(main_area)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Check Out Selected", command=check_out_selected).pack(side="left", padx=10)
    tk.Button(button_frame, text="Extend Selected", command=extend_selected).pack(side="left", padx=10)

    load_checked_in_data()
