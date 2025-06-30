from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class PhotosTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout for this tab
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Photos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Create a grid layout to arrange images in a grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)  # Space between photos

        # List of image file paths
        photo_files = [
            "2.jpg", "3.jpg", "4.jpg",  # replace with your actual images
            "5.jpg", "6.jpg", "7.jpg", "8.jpg", "1.jpg"
        ]
        
        # Iterate through the list of photo files to create image widgets
        for i, photo_file in enumerate(photo_files):
            row = i // 4  # First 4 images will be in the first row, next 3 in the second row
            col = i % 4  # 4 columns

            pixmap = QPixmap(photo_file)
            pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio)  # Adjust size if necessary
            photo_label = QLabel()
            photo_label.setPixmap(pixmap)
            photo_label.setAlignment(Qt.AlignCenter)

            # Add the image label to the grid layout
            grid_layout.addWidget(photo_label, row, col)



        # Add the grid layout to the main layout of the tab
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)
