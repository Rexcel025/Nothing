import tkinter as tk
from tkinter import messagebox, ttk
from database import add_user, get_user
import bcrypt

# Popup register window for login.py
def show_register():
    reg_window = tk.Toplevel()
    reg_window.title("Register New User")

    tk.Label(reg_window, text="Username:").pack(pady=5)
    entry_user = tk.Entry(reg_window)
    entry_user.pack(pady=5)

    tk.Label(reg_window, text="Password:").pack(pady=5)
    entry_pass = tk.Entry(reg_window, show="*")
    entry_pass.pack(pady=5)

    tk.Label(reg_window, text="Role (admin/cashier):").pack(pady=5)
    role_combobox = ttk.Combobox(reg_window, values=["admin", "cashier"], state="readonly")
    role_combobox.current(0)
    role_combobox.pack(pady=5)

    def handle_register():
        username = entry_user.get()
        password = entry_pass.get()
        role = role_combobox.get()

        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required.")
            return

        if get_user(username):
            messagebox.showerror("Error", "Username already exists.")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            add_user(username, hashed_pw, role)
            messagebox.showinfo("Success", "User registered successfully.")
            reg_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")

    tk.Button(reg_window, text="Register", command=handle_register).pack(pady=10)


# Inline register form for dashboard.py
def show_register_in_main_area(main_area):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Register New User", font=("Arial", 16)).pack(pady=10)

    tk.Label(main_area, text="Username:").pack(pady=5)
    entry_user = tk.Entry(main_area)
    entry_user.pack(pady=5)

    tk.Label(main_area, text="Password:").pack(pady=5)
    entry_pass = tk.Entry(main_area, show="*")
    entry_pass.pack(pady=5)

    tk.Label(main_area, text="Role (admin/cashier):").pack(pady=5)
    role_combobox = ttk.Combobox(main_area, values=["admin", "cashier"], state="readonly")
    role_combobox.current(0)
    role_combobox.pack(pady=5)

    def handle_register():
        username = entry_user.get()
        password = entry_pass.get()
        role = role_combobox.get()

        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required.")
            return

        if get_user(username):
            messagebox.showerror("Error", "Username already exists.")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            add_user(username, hashed_pw, role)
            messagebox.showinfo("Success", "User registered successfully.")
            entry_user.delete(0, tk.END)
            entry_pass.delete(0, tk.END)
            role_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")

    tk.Button(main_area, text="Register", command=handle_register).pack(pady=10)
