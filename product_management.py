# product_management.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QDialog, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from database import connect_db


class ProductManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Product Management")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Price"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        #self.table.setStyleSheet("""
            #QTableWidget {
                #background-color: #2b2b2b;
                #color: #f0f0f0;
                #gridline-color: #444;
                #border: 1px solid #444;
            #}
            #QHeaderView::section {
                #background-color: #444;
                #color: #f0f0f0;
                #padding: 4px;
                #border: 1px solid #666;
            #}
            #QTableWidget::item {
                #selection-background-color: #555;
                #selection-color: #ffffff;
            #}
        #""")

        main_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Product")
        add_button.clicked.connect(self.add_product_dialog)
        delete_button = QPushButton("Delete Product")
        delete_button.clicked.connect(self.delete_product)
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        main_layout.addLayout(button_layout)

        self.load_products()

    def load_products(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in products:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(data)))

    def add_product_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Product")
        layout = QVBoxLayout(dialog)

        name_input = QLineEdit()
        price_input = QLineEdit()

        layout.addWidget(QLabel("Product Name:"))
        layout.addWidget(name_input)
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(price_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_product(dialog, name_input.text(), price_input.text()))
        layout.addWidget(save_btn)

        dialog.exec_()

    def save_product(self, dialog, name, price):
        if not name:
            QMessageBox.warning(self, "Input Error", "Product name cannot be empty.")
            return
        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price must be a valid number.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()

        dialog.accept()
        self.load_products()

    def delete_product(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a product to delete.")
            return

        product_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            self.load_products()
