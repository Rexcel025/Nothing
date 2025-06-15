import tkinter as tk
from database import connect_db

status_colors = {
    "vacant": "#2ecc71",     # green
    "occupied": "#e74c3c",   # red
    "reserved": "#f1c40f",   # yellow
}

# List of all rooms you want to display
all_rooms = ["101", "102", "103", "104", "105", "106"]

def get_room_statuses_for_date(date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT room_no, status FROM bookings WHERE date = ?", (date,))
    records = cursor.fetchall()
    conn.close()

    # Default all rooms to vacant
    room_status = {room: "vacant" for room in all_rooms}

    for room_no, status in records:
        room_status[room_no] = status.lower()

    return room_status

def show_room_map(main_area, selected_date, on_room_click):
    for widget in main_area.winfo_children():
        widget.destroy()

    tk.Label(main_area, text=f"Room Map - {selected_date}", font=("Arial", 16)).pack(pady=10)

    # Fetch live statuses from DB
    room_status_data = get_room_statuses_for_date(selected_date)

    grid_frame = tk.Frame(main_area)
    grid_frame.pack(pady=10)

    def refresh_map():
        show_room_map(main_area, selected_date, on_room_click)

    for idx, room_no in enumerate(all_rooms):
        status = room_status_data.get(room_no, "vacant")
        color = status_colors.get(status, "#bdc3c7")  # fallback to gray

        btn = tk.Button(
            grid_frame,
            text=f"Room {room_no}\n({status})",
            bg=color,
            width=15,
            height=4,
            command=lambda rn=room_no: on_room_click(selected_date, rn, refresh_map)
        )
        btn.grid(row=idx // 3, column=idx % 3, padx=10, pady=10)
