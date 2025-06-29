# register.py
# This file implements the RegisterWidget, which allows users to register new users in the system.
# It includes fields for username, password, and role, and displays a list of existing users
# for management. The widget uses PyQt5 for the GUI and interacts with a SQLite database
# for user management. It includes functionality to add new users, check for existing usernames,
# and remove users from the system. Passwords are hashed using bcrypt for security.
# The database operations are handled in the database.py file.
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QListWidget
)
from database import add_user, get_user, connect_db
import bcrypt

class RegisterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Register New User")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        form_layout = QVBoxLayout()

        # Username
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        self.username_input = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_input)
        form_layout.addLayout(user_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_input)
        form_layout.addLayout(pass_layout)

        # Role
        role_layout = QHBoxLayout()
        role_label = QLabel("Role:")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "cashier"])
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        form_layout.addLayout(role_layout)

        # Register Button
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_user)
        form_layout.addWidget(register_button)

        layout.addLayout(form_layout)

        # User List
        list_title = QLabel("Existing Users:")
        layout.addWidget(list_title)

        self.user_list = QListWidget()
        self.load_users()
        layout.addWidget(self.user_list)

        # Remove Button
        remove_button = QPushButton("Remove Selected User")
        remove_button.clicked.connect(self.remove_user)
        layout.addWidget(remove_button)

        self.setLayout(layout)

    def load_users(self):
        self.user_list.clear()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.user_list.addItem(user[0])

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if get_user(username):
            QMessageBox.warning(self, "Error", "Username already exists.")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        if add_user(username, hashed_pw, role):
            QMessageBox.information(self, "Success", "User registered.")
            self.load_users()  # Refresh list
            self.username_input.clear()
            self.password_input.clear()
            self.role_combo.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", "Failed to register user.")

    def remove_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Select a user to remove.")
            return

        username = selected_items[0].text()
        confirm = QMessageBox.question(self, "Confirm Removal",
                                       f"Remove user '{username}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            self.load_users()  # Refresh list
            QMessageBox.information(self, "Removed", f"User '{username}' removed.")
