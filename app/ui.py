from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal

class MainWindow(QWidget):
    worker_progress_signal = pyqtSignal(str)  # Signal for progress messages

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.load_data_button = QPushButton("Load Data")
        self.file_table = QTableWidget()
        self.layout.addWidget(self.load_data_button)
        self.layout.addWidget(self.file_table)
        self.setLayout(self.layout)
        
        # Connect progress messages to the main window
        self.load_data_button.clicked.connect(self.handle_load_data)

    def handle_load_data(self):
        self.worker_progress_signal.emit("Button clicked: Starting data load")

    def update_file_table(self, file_list):
        self.file_table.setRowCount(len(file_list))
        self.file_table.setColumnCount(3)  # Example columns: Name, Size, Type
        self.file_table.setHorizontalHeaderLabels(['Name', 'Size', 'Type'])

        for row, file in enumerate(file_list):
            self.file_table.setItem(row, 0, QTableWidgetItem(file['name']))
            self.file_table.setItem(row, 1, QTableWidgetItem(str(file['size'])))
            self.file_table.setItem(row, 2, QTableWidgetItem(file['type']))
