# login.py
import sys
import bcrypt
from database import get_user
from register_popup import RegisterPopup
from database import initialize_db, seed_initial_data
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication  
)

class LoginWindow(QMainWindow):
    initialize_db()
    seed_initial_data()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hotel System Login")
        self.setGeometry(100, 100, 340, 220)

        # --- Main central widget ---
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(22)
        layout.setContentsMargins(38, 36, 38, 36)

        # Username
        user_row = QHBoxLayout()
        user_label = QLabel("Username")
        self.entry_user = QLineEdit()
        user_row.addWidget(user_label)
        user_row.addWidget(self.entry_user)
        layout.addLayout(user_row)

        # Password
        pass_row = QHBoxLayout()
        pass_label = QLabel("Password ")
        self.entry_pass = QLineEdit()
        self.entry_pass.setEchoMode(QLineEdit.Password)
        pass_row.addWidget(pass_label)
        pass_row.addWidget(self.entry_pass)
        layout.addLayout(pass_row)

        # --- Button Group ---
        button_group = QVBoxLayout()
        button_group.setSpacing(6)  

        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(160)
        self.login_button.clicked.connect(self.handle_login)
        button_group.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.register_button = QPushButton("Register ")
        self.register_button.setFixedWidth(160)
        self.register_button.clicked.connect(self.show_register_window)
        self.register_button.setEnabled(False)
        button_group.addWidget(self.register_button, alignment=Qt.AlignCenter)

        layout.addLayout(button_group)

    def handle_login(self):
        username = self.entry_user.text()
        password = self.entry_pass.text()

        user = get_user(username)
        if user and bcrypt.checkpw(password.encode(), user[2]):
       
            from dashboard import Dashboard
            self.dashboard = Dashboard(user[3])
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Wrong username or password.")

    def show_register_window(self):
        dialog = RegisterPopup(self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)


    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())

    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
