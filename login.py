# login.py
from dashboard import open_dashboard

import tkinter as tk
from tkinter import messagebox
from database import get_user
import bcrypt
from register import show_register

def login_screen():
    def handle_login():
        username = entry_user.get()
        password = entry_pass.get()

        user = get_user(username)
        if user and bcrypt.checkpw(password.encode(), user[2]):
            root.destroy()
            open_dashboard(user[3])

            if user[3] == "admin":
                show_register_button()

        else:
            messagebox.showerror("Login Failed", "Wrong username or password.")

    def show_register_button():
        btn_register.config(state=tk.NORMAL)

    root = tk.Tk()
    root.title("Hotel System Login")

    tk.Label(root, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(root, text="Password").grid(row=1, column=0, padx=10, pady=5)

    entry_user = tk.Entry(root)
    entry_pass = tk.Entry(root, show="*")
    entry_user.grid(row=0, column=1, padx=10, pady=5)
    entry_pass.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(root, text="Login", command=handle_login).grid(row=2, columnspan=2, pady=5)

    btn_register = tk.Button(root, text="Register New User", command=show_register, state=tk.DISABLED)
    btn_register.grid(row=3, columnspan=2, pady=5)

    root.mainloop()
