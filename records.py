from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QDialog, QLineEdit, QDateEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtPrintSupport import QPrinter  
from PyQt5.QtGui import QTextDocument      
from database import connect_db, get_all_products
from datetime import datetime, timedelta

class RecordsTab(QWidget):
    def __init__(self, user_role):
        super().__init__()
        self.user_role = user_role
        self.selected_date = datetime.now().date()
        self.selected_booking_id = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Booking Records")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Date navigation
        date_layout = QHBoxLayout()
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.dateChanged.connect(self.date_changed)

        prev_btn = QPushButton("< Previous")
        prev_btn.clicked.connect(self.prev_day)
        next_btn = QPushButton("Next >")
        next_btn.clicked.connect(self.next_day)

        date_layout.addWidget(prev_btn)
        date_layout.addWidget(self.date_picker)
        date_layout.addWidget(next_btn)
        layout.addLayout(date_layout)

        # Booking table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Date", "Room", "Name", "Check-In Time",
            "Check-Out Time", "Check-Out Date", "Status", "Room Cost", "Encoded By", "Product Total"
        ])
        self.table.cellClicked.connect(self.show_product_details)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # Summary
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        # Product table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["Product", "Price", "Quantity", "ID (hidden)"])
        layout.addWidget(self.product_table)

        # Buttons for quantity change
        qty_btn_layout = QHBoxLayout()
        plus_btn = QPushButton("+")
        plus_btn.clicked.connect(lambda: self.adjust_quantity(1))
        minus_btn = QPushButton("-")
        minus_btn.clicked.connect(lambda: self.adjust_quantity(-1))
        qty_btn_layout.addWidget(plus_btn)
        qty_btn_layout.addWidget(minus_btn)
        layout.addLayout(qty_btn_layout)

        # Add product button
        add_product_btn = QPushButton("+ Add Product")
        add_product_btn.clicked.connect(self.add_product_popup)
        layout.addWidget(add_product_btn)

        # Print/Save to PDF button
        self.print_btn = QPushButton("Print/Save to PDF") 
        self.print_btn.clicked.connect(self.print_to_pdf)   
        layout.addWidget(self.print_btn)                   

    def date_changed(self, new_date):
        self.selected_date = new_date.toPyDate()
        self.load_data()

    def prev_day(self):
        self.selected_date -= timedelta(days=1)
        self.date_picker.setDate(QDate(self.selected_date.year, self.selected_date.month, self.selected_date.day))
        self.load_data()

    def next_day(self):
        self.selected_date += timedelta(days=1)
        self.date_picker.setDate(QDate(self.selected_date.year, self.selected_date.month, self.selected_date.day))
        self.load_data()

    def load_data(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.date, b.room_no, b.customer_name, b.checkin_time,
                   b.checkout_date, b.checkout_time, b.status, b.total_cost, u.username
            FROM bookings b
            LEFT JOIN users u ON b.encoded_by = u.id
            WHERE b.date = ?
        """, (self.selected_date.strftime('%Y-%m-%d'),))
        bookings = cursor.fetchall()

        room_income = 0
        product_income = 0

        self.table.setRowCount(len(bookings))

        for row_idx, booking in enumerate(bookings):
            booking_id = booking[0] 
            room_total = booking[8]  

            # Calculate product total per booking
            cursor.execute("""
                SELECT p.price, bp.quantity
                FROM booking_products bp
                JOIN products p ON bp.product_id = p.id
                WHERE bp.booking_id = ?
            """, (booking_id,))
            product_rows = cursor.fetchall()
            product_total = sum(price * qty for price, qty in product_rows)

            room_income += room_total
            product_income += product_total

            # Populate row
            for col_idx, item in enumerate(booking):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
            self.table.setItem(row_idx, 10, QTableWidgetItem(f"₱{product_total:.2f}"))  

        conn.close()

        total_income = room_income + product_income
        self.summary_label.setText(
            f"Total Bookings: {len(bookings)} | Room Income: ₱{room_income:.2f} | Product Income: ₱{product_income:.2f} | Total Income: ₱{total_income:.2f}"
        )

    def show_product_details(self, row, _):
        booking_id = int(self.table.item(row, 0).text())
        self.selected_booking_id = booking_id

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.price, bp.quantity, p.id
            FROM booking_products bp
            JOIN products p ON bp.product_id = p.id
            WHERE bp.booking_id = ?
        """, (booking_id,))
        products = cursor.fetchall()
        conn.close()

        self.product_table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            for col_idx, item in enumerate(product[:3]):
                self.product_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
            self.product_table.setItem(row_idx, 3, QTableWidgetItem(str(product[3])))  

    def adjust_quantity(self, change):
        selected = self.product_table.currentRow()
        if selected == -1 or self.selected_booking_id is None:
            return

        product_id = int(self.product_table.item(selected, 3).text())
        quantity = int(self.product_table.item(selected, 2).text())
        new_qty = quantity + change

        conn = connect_db()
        cursor = conn.cursor()
        if new_qty < 1:
            cursor.execute("""
                DELETE FROM booking_products WHERE booking_id = ? AND product_id = ?
            """, (self.selected_booking_id, product_id))
        else:
            cursor.execute("""
                UPDATE booking_products SET quantity = ? WHERE booking_id = ? AND product_id = ?
            """, (new_qty, self.selected_booking_id, product_id))
        conn.commit()
        conn.close()

        self.show_product_details(self.table.currentRow(), 0)
        self.load_data()  

    def add_product_popup(self):
        if self.selected_booking_id is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Product")

        layout = QVBoxLayout(dialog)
        product_cb = QComboBox()
        all_products = get_all_products()
        product_cb.addItems([prod[1] for prod in all_products])
        layout.addWidget(QLabel("Select Product:"))
        layout.addWidget(product_cb)

        qty_input = QLineEdit("1")
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(qty_input)

        def save_product():
            product_name = product_cb.currentText()
            quantity = qty_input.text()
            if not quantity.isdigit() or int(quantity) <= 0:
                QMessageBox.warning(self, "Invalid Input", "Enter a valid quantity.")
                return

            quantity = int(quantity)
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            product_id = cursor.fetchone()[0]

            cursor.execute("""
                SELECT id FROM booking_products WHERE booking_id = ? AND product_id = ?
            """, (self.selected_booking_id, product_id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE booking_products SET quantity = quantity + ? WHERE booking_id = ? AND product_id = ?
                """, (quantity, self.selected_booking_id, product_id))
            else:
                cursor.execute("""
                    INSERT INTO booking_products (booking_id, product_id, quantity) VALUES (?, ?, ?)
                """, (self.selected_booking_id, product_id, quantity))
            conn.commit()
            conn.close()
            dialog.accept()

            self.show_product_details(self.table.currentRow(), 0)
            self.load_data()  

        save_btn = QPushButton("Add")
        save_btn.clicked.connect(save_product)
        layout.addWidget(save_btn)
        dialog.exec_()


    def print_to_pdf(self):  
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)", options=options
        )
        if not filename:
            return

        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'


        html = "<h2>Booking Records for {}</h2>".format(self.selected_date.strftime('%Y-%m-%d'))
        html += "<table border='1' cellspacing='0' cellpadding='4'><tr>"

        headers = [
            "ID", "Date", "Room", "Name", "Check-In Time",
            "Check-Out Time", "Check-Out Date", "Status", "Room Cost", "Encoded By", "Product Total"
        ]
        for h in headers:
            html += f"<th>{h}</th>"
        html += "</tr>"

        # Data rows
        for row in range(self.table.rowCount()):
            html += "<tr>"
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                html += f"<td>{item.text() if item else ''}</td>"
            html += "</tr>"
        html += "</table>"

        # Summary
        html += f"<br><b>{self.summary_label.text()}</b>"


        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)

        doc.print_(printer)

        QMessageBox.information(self, "Exported", f"PDF saved to:\n{filename}")
