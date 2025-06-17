import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db

def show_product_management(main_area):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Product Management", font=("Arial", 16)).pack(pady=10)

    # Treeview
    tree = ttk.Treeview(main_area, columns=("ID", "Name", "Price"), show="headings")
    for col in ("ID", "Name", "Price"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)
    tree.pack(expand=True, fill="both", padx=10, pady=5)

    def load_products():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()

        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    def add_product():
        def save_product():
            name = name_entry.get()
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Invalid", "Price must be a number.")
                return

            if not name:
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
            conn.commit()
            conn.close()
            add_win.destroy()
            load_products()

        add_win = tk.Toplevel()
        add_win.title("Add Product")

        tk.Label(add_win, text="Product Name:").pack(pady=5)
        name_entry = tk.Entry(add_win)
        name_entry.pack(pady=5)

        tk.Label(add_win, text="Price:").pack(pady=5)
        price_entry = tk.Entry(add_win)
        price_entry.pack(pady=5)

        tk.Button(add_win, text="Save", command=save_product).pack(pady=10)

    def delete_product():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to delete.")
            return

        product_id = tree.item(selected[0])["values"][0]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

        load_products()

    # Buttons
    tk.Button(main_area, text="Add Product", command=add_product).pack(side="left", padx=10, pady=10)
    tk.Button(main_area, text="Delete Product", command=delete_product).pack(side="left", padx=10, pady=10)

    load_products()
