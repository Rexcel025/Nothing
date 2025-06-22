from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
import sys
import bcrypt
from database import get_user
from dashboard import Dashboard  # Import Dashboard class directly
from register_popup import RegisterPopup
from database import initialize_db, seed_initial_data


class LoginWindow(QMainWindow):
    initialize_db()
    seed_initial_data()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hotel System Login")
        self.setGeometry(100, 100, 300, 200)

        self.label_user = QLabel("Username", self)
        self.label_user.move(20, 20)

        self.entry_user = QLineEdit(self)
        self.entry_user.move(100, 20)

        self.label_pass = QLabel("Password", self)
        self.label_pass.move(20, 60)

        self.entry_pass = QLineEdit(self)
        self.entry_pass.setEchoMode(QLineEdit.Password)
        self.entry_pass.move(100, 60)

        self.login_button = QPushButton("Login", self)
        self.login_button.move(100, 100)
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton("Register New User", self)
        self.register_button.move(100, 140)
        self.register_button.clicked.connect(self.show_register_window)
        self.register_button.setEnabled(True)

    def handle_login(self):
        username = self.entry_user.text()
        password = self.entry_pass.text()

        user = get_user(username)
        if user and bcrypt.checkpw(password.encode(), user[2]):
            # OPEN DASHBOARD WINDOW
            self.dashboard = Dashboard(user[3])  # Create Dashboard instance
            self.dashboard.show()
            self.close()  # Close login window
        else:
            QMessageBox.critical(self, "Login Failed", "Wrong username or password.")

    def show_register_window(self):
        dialog = RegisterPopup(self)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
