import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint


class ImageSelector(QWidget):
    def __init__(self, image_paths):
        super().__init__()
        self.image_paths = image_paths
        self.selected_images = set()  # Store selected image paths
        self.current_page = 0  # Current page index (pagination)
        self.images_per_page = 16  # Images to display per page
        self.total_pages = (len(self.image_paths) + self.images_per_page - 1) // self.images_per_page  # Total pages
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Selector")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Grid layout for images
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        # Add navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_page)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)

        # Add Save button
        save_button = QPushButton("Save Selected Images")
        save_button.clicked.connect(self.save_selected_images)
        self.layout.addWidget(save_button)

        # Show the first page of images
        self.show_page()

    def show_page(self):
        # Clear the grid layout before adding new images
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        start_index = self.current_page * self.images_per_page
        end_index = min(start_index + self.images_per_page, len(self.image_paths))

        # Add images to the grid
        for index, image_path in enumerate(self.image_paths[start_index:end_index]):
            image_label = ClickableLabel(image_path)
            image_label.setPixmap(QPixmap(image_path).scaled(100, 100, Qt.KeepAspectRatio))
            image_label.clicked.connect(self.toggle_selection)
            image_label.rightClicked.connect(self.view_full_image)

            row, col = divmod(index, 4)  # 4x4 grid
            self.grid_layout.addWidget(image_label, row, col)

        # Enable/disable buttons based on page number
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def show_next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()

    def toggle_selection(self, image_path, label):
        if image_path in self.selected_images:
            self.selected_images.remove(image_path)
            label.show_tick(False)
        else:
            self.selected_images.add(image_path)
            label.show_tick(True)

    def save_selected_images(self):
        # Convert the set of selected image paths to a list
        selected_images_list = list(self.selected_images)
        
        # Define the path to save the JSON file
        save_path = os.path.join(os.getcwd(), "selected_images.json")
        
        # Write the selected image paths to the JSON file
        with open(save_path, "w") as f:
            json.dump(selected_images_list, f, indent=4)
        
        print(f"Selected images saved to {save_path}")

    def view_full_image(self, image_path):
        # Create and display the full-size image view dialog
        dialog = FullImageDialog(image_path)
        dialog.exec_()


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str, object)
    rightClicked = pyqtSignal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.tick_shown = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path, self)
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit(self.image_path)

    def show_tick(self, show):
        self.tick_shown = show
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.tick_shown:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0), 5))  # Red color tick
#            painter.setPen(QPen(QColor(0, 255, 0), 5))  # Green color tick
            painter.drawText(self.rect().topRight() - QPoint(20, -20), "✓")  # Fixed QPoint reference
            painter.end()


class FullImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Full-Size Image View")
        self.setGeometry(100, 100, 800, 600)  # Set initial window size
        self.image_path = image_path

        layout = QHBoxLayout()
        self.label = QLabel(self)
        pixmap = QPixmap(self.image_path)
        self.label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio))
        layout.addWidget(self.label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Get all image files in the directory
    image_directory = "/home/sab/Pictures/Screenshots/"
    image_paths = [os.path.join(image_directory, f) for f in os.listdir(image_directory)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    if not image_paths:
        print("No image files found in the specified directory.")
        sys.exit()

    selector = ImageSelector(image_paths)
    selector.show()
    sys.exit(app.exec_())

