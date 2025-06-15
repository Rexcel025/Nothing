import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime

def show_records_screen(root, user_role):
    records_window = tk.Toplevel(root)
    records_window.title("Booking Records")

    tk.Label(records_window, text="Booking Records", font=("Arial", 16)).pack(pady=10)

    tree = ttk.Treeview(records_window, columns=(
        "ID", "Date", "Room", "Name", "Check-In", "Check-Out", "Status", "Status Now"), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.pack(expand=True, fill="both", padx=10, pady=5)

    def load_data():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        rows = cursor.fetchall()
        conn.close()

        tree.delete(*tree.get_children())

        now = datetime.now()
        for row in rows:
            booking_id, date_str, room_no, name, checkin, checkout, status = row
            try:
                checkout_dt = datetime.strptime(f"{date_str} {checkout}", "%Y-%m-%d %H:%M")
                status_now = "Checked-out" if now > checkout_dt else "Checked-in"
            except ValueError:
                status_now = "Invalid time"
            tree.insert("", "end", values=(booking_id, date_str, room_no, name, checkin, checkout, status, status_now))

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a booking to delete.")
            return
        booking_id = tree.item(selected[0])["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        load_data()
        messagebox.showinfo("Deleted", "Booking deleted successfully.")

    def edit_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a booking to edit.")
            return
        values = tree.item(selected[0])["values"]

        edit_window = tk.Toplevel(records_window)
        edit_window.title("Edit Booking")

        labels = ["Date", "Room No", "Customer Name", "Check-in", "Check-out", "Status"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(edit_window, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(edit_window)
            entry.insert(0, values[i + 1])
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save_changes():
            new_values = [e.get() for e in entries]
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bookings SET date=?, room_no=?, customer_name=?,
                checkin_time=?, checkout_time=?, status=? WHERE id=?
            """, (*new_values, values[0]))
            conn.commit()
            conn.close()
            load_data()
            edit_window.destroy()
            messagebox.showinfo("Success", "Booking updated successfully.")

        tk.Button(edit_window, text="Save", command=save_changes).grid(row=len(labels), column=0, columnspan=2, pady=10)

    # Admin-only buttons
    if user_role in ("admin", "cashier"):
        btn_frame = tk.Frame(records_window)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Edit Selected", command=edit_selected).pack(side="left", padx=10)

        if user_role == "admin":
            tk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side="left", padx=10)

    load_data()
