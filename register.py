# register.py

import tkinter as tk
from tkinter import messagebox
import bcrypt
from database import add_user

def show_register():
    def handle_register():
        username = entry_user.get()
        password = entry_pass.get()
        role = role_var.get()

        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required.")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        success = add_user(username, hashed_pw, role)

        if success:
            messagebox.showinfo("Success", f"{role.capitalize()} registered.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Username already exists.")

    win = tk.Toplevel()
    win.title("Register New User")

    tk.Label(win, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(win, text="Password").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(win, text="Role").grid(row=2, column=0, padx=10, pady=5)

    entry_user = tk.Entry(win)
    entry_pass = tk.Entry(win, show="*")
    role_var = tk.StringVar(value="cashier")

    entry_user.grid(row=0, column=1, padx=10)
    entry_pass.grid(row=1, column=1, padx=10)
    tk.OptionMenu(win, role_var, "admin", "cashier").grid(row=2, column=1)

    tk.Button(win, text="Register", command=handle_register).grid(row=3, columnspan=2, pady=10)
