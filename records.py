import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db, get_all_products
from datetime import datetime, timedelta

def show_records_tab(main_area, user_role):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Booking Records", font=("Arial", 16)).pack(pady=10)

    date_frame = tk.Frame(main_area)
    date_frame.pack()

    selected_date = [datetime.now().date()]

    def update_date_label():
        date_label.config(text=f"Date: {selected_date[0]}")

    def prev_day():
        selected_date[0] -= timedelta(days=1)
        load_data()

    def next_day():
        selected_date[0] += timedelta(days=1)
        load_data()

    prev_btn = tk.Button(date_frame, text="< Previous", command=prev_day)
    prev_btn.pack(side="left", padx=5)

    date_label = tk.Label(date_frame, text="")
    date_label.pack(side="left", padx=5)

    next_btn = tk.Button(date_frame, text="Next >", command=next_day)
    next_btn.pack(side="left", padx=5)

    columns = ("ID", "Date", "Room", "Name", "Check-In Time", "Check-Out Time", "Check-Out Date", "Status", "Total Cost", "Encoded By")
    tree = ttk.Treeview(main_area, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.pack(expand=True, fill="both", padx=10, pady=5)

    summary_label = tk.Label(main_area, text="")
    summary_label.pack(pady=5)

    details_frame = tk.LabelFrame(main_area, text="Products Availed")
    details_frame.pack(fill="x", padx=10, pady=5)

    details_tree = ttk.Treeview(details_frame, columns=("Product", "Price", "Quantity"), show="headings", height=5)
    details_tree.heading("Product", text="Product")
    details_tree.heading("Price", text="Price")
    details_tree.heading("Quantity", text="Quantity")
    details_tree.column("Product", width=150)
    details_tree.column("Price", width=80, anchor="center")
    details_tree.column("Quantity", width=80, anchor="center")
    details_tree.pack(fill="both", padx=5, pady=5)

    qty_buttons_frame = tk.Frame(details_frame)
    qty_buttons_frame.pack(pady=5)

    plus_btn = tk.Button(qty_buttons_frame, text="+", width=5)
    plus_btn.pack(side="left", padx=5)

    minus_btn = tk.Button(qty_buttons_frame, text="-", width=5)
    minus_btn.pack(side="left", padx=5)

    add_product_btn = tk.Button(details_frame, text="+ Add Product", state="disabled")
    add_product_btn.pack(pady=5)

    selected_booking_id = [None]

    def load_data():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.date, b.room_no, b.customer_name, b.checkin_time,
                   b.checkout_date, b.checkout_time, b.status, b.total_cost, u.username
            FROM bookings b
            LEFT JOIN users u ON b.encoded_by = u.id
            WHERE b.date = ?
        """, (selected_date[0].strftime('%Y-%m-%d'),))
        bookings = cursor.fetchall()
        conn.close()

        tree.delete(*tree.get_children())
        total_income = 0
        total_bookings = len(bookings)

        for booking in bookings:
            total_income += booking[8]
            tree.insert("", "end", values=booking)

        summary_label.config(text=f"Total Bookings: {total_bookings} | Total Income: ₱{total_income:.2f}")
        update_date_label()

    def show_product_details(event):
        selected = tree.selection()
        if not selected:
            add_product_btn.config(state="disabled")
            return
        booking_id = tree.item(selected[0])["values"][0]
        selected_booking_id[0] = booking_id
        add_product_btn.config(state="normal")

        details_tree.delete(*details_tree.get_children())
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.price, bp.quantity, p.id
            FROM booking_products bp
            JOIN products p ON bp.product_id = p.id
            WHERE bp.booking_id = ?
        """, (booking_id,))
        products = cursor.fetchall()
        conn.close()

        for product in products:
            details_tree.insert("", "end", values=(product[0], product[1], product[2]), tags=(product[3],))

    def adjust_quantity(change):
        selected = details_tree.selection()
        if not selected or selected_booking_id[0] is None:
            return
        item = details_tree.item(selected[0])
        product_id = details_tree.item(selected[0], "tags")[0]
        quantity = int(item['values'][2])
        new_qty = quantity + change

        conn = connect_db()
        cursor = conn.cursor()
        if new_qty < 1:
            cursor.execute("""
                DELETE FROM booking_products
                WHERE booking_id = ? AND product_id = ?
            """, (selected_booking_id[0], product_id))
        else:
            cursor.execute("""
                UPDATE booking_products
                SET quantity = ?
                WHERE booking_id = ? AND product_id = ?
            """, (new_qty, selected_booking_id[0], product_id))
        conn.commit()
        conn.close()

        show_product_details(None)

    def add_product_popup():
        if selected_booking_id[0] is None:
            return

        def save_product():
            product_name = product_var.get()
            quantity = qty_var.get()
            if not product_name or not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showwarning("Invalid Input", "Select a product and enter a valid quantity.")
                return

            quantity = int(quantity)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Product not found.")
                conn.close()
                return
            product_id = result[0]

            cursor.execute("""
                SELECT id FROM booking_products
                WHERE booking_id = ? AND product_id = ?
            """, (selected_booking_id[0], product_id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE booking_products
                    SET quantity = quantity + ?
                    WHERE booking_id = ? AND product_id = ?
                """, (quantity, selected_booking_id[0], product_id))
            else:
                cursor.execute("""
                    INSERT INTO booking_products (booking_id, product_id, quantity)
                    VALUES (?, ?, ?)
                """, (selected_booking_id[0], product_id, quantity))

            conn.commit()
            conn.close()
            top.destroy()
            show_product_details(None)

        top = tk.Toplevel(main_area)
        top.title("Add Product")

        tk.Label(top, text="Select Product:").pack(padx=10, pady=5)
        product_var = tk.StringVar()
        product_cb = ttk.Combobox(top, textvariable=product_var)
        product_cb['values'] = [prod[1] for prod in get_all_products()]
        product_cb.pack(padx=10, pady=5)

        tk.Label(top, text="Quantity:").pack(padx=10, pady=5)
        qty_var = tk.StringVar(value="1")
        tk.Entry(top, textvariable=qty_var).pack(padx=10, pady=5)

        tk.Button(top, text="Add", command=save_product).pack(pady=10)

    plus_btn.config(command=lambda: adjust_quantity(1))
    minus_btn.config(command=lambda: adjust_quantity(-1))
    add_product_btn.config(command=add_product_popup)

    tree.bind("<<TreeviewSelect>>", show_product_details)
    load_data()
