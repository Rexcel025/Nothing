import tkinter as tk
from tkinter import messagebox
from database import connect_db

def show_room_management(main_area):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text="Room Management", font=("Arial", 16)).pack(pady=10)

    form_frame = tk.Frame(main_area)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Room No:").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(form_frame, text="Base Price:").grid(row=1, column=0, padx=5, pady=5)

    entry_room_no = tk.Entry(form_frame)
    entry_price = tk.Entry(form_frame)
    entry_room_no.grid(row=0, column=1, padx=5, pady=5)
    entry_price.grid(row=1, column=1, padx=5, pady=5)

    def add_room():
        room_no = entry_room_no.get().strip()
        try:
            price = float(entry_price.get())
            if room_no == "":
                raise ValueError("Room No cannot be empty.")
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO room_prices (room_no, base_price) VALUES (?, ?)", (room_no, price))
            conn.commit()
            messagebox.showinfo("Success", "Room added successfully.")
            load_rooms()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def update_room():
        room_no = entry_room_no.get().strip()
        try:
            price = float(entry_price.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid price.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE room_prices SET base_price = ? WHERE room_no = ?", (price, room_no))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room updated successfully.")
        load_rooms()

    def delete_room():
        room_no = entry_room_no.get().strip()

        if room_no == "":
            messagebox.showerror("Invalid Input", "Enter Room No to delete.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM room_prices WHERE room_no = ?", (room_no,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room deleted successfully.")
        load_rooms()

    tk.Button(form_frame, text="Add Room", command=add_room).grid(row=2, column=0, padx=5, pady=5)
    tk.Button(form_frame, text="Update Price", command=update_room).grid(row=2, column=1, padx=5, pady=5)
    tk.Button(form_frame, text="Remove Room", command=delete_room).grid(row=2, column=2, padx=5, pady=5)

    list_frame = tk.Frame(main_area)
    list_frame.pack(pady=10)

    tk.Label(list_frame, text="Existing Rooms:").pack()

    room_listbox = tk.Listbox(list_frame, width=40)
    room_listbox.pack()

    def load_rooms():
        room_listbox.delete(0, tk.END)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT room_no, base_price FROM room_prices")
        for room_no, price in cursor.fetchall():
            room_listbox.insert(tk.END, f"Room {room_no}: ₱{price}")
        conn.close()

    load_rooms()

