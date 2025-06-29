
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from database import add_user, get_user
import bcrypt

class RegisterPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New User")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "cashier"])
        layout.addWidget(self.role_combo)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

        self.setLayout(layout)

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
        add_user(username, hashed_pw, role)
        QMessageBox.information(self, "Success", "User registered successfully.")
        self.accept()  
