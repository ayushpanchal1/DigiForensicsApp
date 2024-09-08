from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import pyqtSignal

class MainWindow(QWidget):
    worker_progress_signal = pyqtSignal(str)  # Signal for progress messages

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.textChanged.connect(self.handle_search)

        self.load_data_button = QPushButton("Load Data")
        self.file_table = QTableWidget()

        # Layout setup
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.load_data_button)
        self.layout.addWidget(self.file_table)
        self.setLayout(self.layout)

        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(['Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])
        self.file_table.setSortingEnabled(True)  # Enable sorting

        # Connect progress messages to the main window
        self.load_data_button.clicked.connect(self.handle_load_data)

    def handle_load_data(self):
        self.worker_progress_signal.emit("Button clicked: Starting data load")

    def handle_search(self, text):
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)  # Search in the 'Path' column
            if item and text.lower() in item.text().lower():
                self.file_table.setRowHidden(row, False)
            else:
                self.file_table.setRowHidden(row, True)

    def update_file_table(self, file_list):
        self.file_table.setRowCount(len(file_list))
        self.file_table.setColumnCount(7)  # Update column count
        self.file_table.setHorizontalHeaderLabels(['Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])

        for row, file in enumerate(file_list):
            self.file_table.setItem(row, 0, QTableWidgetItem(file['path']))
            self.file_table.setItem(row, 1, QTableWidgetItem(str(file['size'])))
            self.file_table.setItem(row, 2, QTableWidgetItem(file['modified_time']))
            self.file_table.setItem(row, 3, QTableWidgetItem(file['created_time']))
            self.file_table.setItem(row, 4, QTableWidgetItem(file['access_time']))
            self.file_table.setItem(row, 5, QTableWidgetItem(file['sha256']))
            self.file_table.setItem(row, 6, QTableWidgetItem('Yes' if file['is_suspicious'] else 'No'))
