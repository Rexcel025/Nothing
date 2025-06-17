import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database import connect_db

def show_checked_in_tab(main_area):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Checked-In Customers", font=("Arial", 16)).pack(pady=10)

    tree = ttk.Treeview(main_area, columns=(
        "ID", "Date", "Room", "Name", "Check-In", "Check-Out", "Check-Out Date", "Status", "Total Cost", "Current Status"), show="headings")

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
                check_out_dt = datetime.strptime(f"{row[6]} {row[5]}", "%Y-%m-%d %H:%M")
                current_status = "Overstayed" if now > check_out_dt else "Checked In"
            except Exception as e:
                current_status = f"Invalid Time: {e}"

            total_cost = f"₱{row[8]:.2f}" if row[8] is not None else "₱0.00"
            tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], total_cost, current_status))

    load_checked_in_data()

    def extend_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a booking to extend.")
            return

        values = tree.item(selected[0])["values"]

        extend_window = tk.Toplevel()
        extend_window.title("Extend Booking")

        tk.Label(extend_window, text="New Check-Out Date:").pack(pady=5)
        date_entry = DateEntry(extend_window, date_pattern='yyyy-mm-dd')
        date_entry.set_date(values[6])
        date_entry.pack(pady=5)

        tk.Label(extend_window, text="New Check-Out Time (HH:MM):").pack(pady=5)
        time_entry = tk.Entry(extend_window)
        time_entry.insert(0, values[5])
        time_entry.pack(pady=5)

        def save_new_time():
            new_date = date_entry.get_date().strftime("%Y-%m-%d")
            new_time = time_entry.get()

            try:
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Invalid Time", "Time must be in HH:MM format.")
                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT checkin_time, date, room_no FROM bookings WHERE id = ?", (values[0],))
            checkin_time, checkin_date, room_no = cursor.fetchone()

            checkin_dt = datetime.strptime(f"{checkin_date} {checkin_time}", "%Y-%m-%d %H:%M")
            new_checkout_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
            if new_checkout_dt <= checkin_dt:
                messagebox.showerror("Invalid", "New checkout must be after check-in.")
                conn.close()
                return

            cursor.execute("SELECT base_price FROM room_prices WHERE room_no = ?", (room_no,))
            base_price = cursor.fetchone()[0]

            duration_hours = (new_checkout_dt - checkin_dt).total_seconds() / 3600
            if duration_hours <= 3:
                total_cost = base_price
            else:
                extra_hours = duration_hours - 3
                total_cost = base_price + (extra_hours * (base_price / 3))

            cursor.execute("""
                UPDATE bookings SET checkout_time = ?, checkout_date = ?, total_cost = ?
                WHERE id = ?
            """, (new_time, new_date, total_cost, values[0]))
            conn.commit()
            conn.close()

            extend_window.destroy()
            load_checked_in_data()
            messagebox.showinfo("Success", f"Booking extended. New total cost: ₱{int(total_cost)}")

        tk.Button(extend_window, text="Save", command=save_new_time).pack(pady=10)

    def checkout_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a booking to check out.")
            return

        values = tree.item(selected[0])["values"]
        booking_id = values[0]

        confirm = messagebox.askyesno("Confirm Check-Out", "Are you sure you want to check out this booking?")
        if not confirm:
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'vacant' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        load_checked_in_data()
        messagebox.showinfo("Checked Out", "The booking has been checked out successfully.")

    button_frame = tk.Frame(main_area)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Extend Booking", command=extend_selected).pack(side="left", padx=5)
    tk.Button(button_frame, text="Check Out", command=checkout_selected).pack(side="left", padx=5)

def reload_checked_in_data(main_area):
    show_checked_in_tab(main_area)
