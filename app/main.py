import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from forensic import ForensicAnalyzer

class WorkerThread(QThread):
    progress_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        self.progress_signal.emit("Worker thread started")
        self.progress_signal.emit("Starting file listing")
        analyzer = ForensicAnalyzer()
        files = analyzer.list_files(self.directory)
        self.progress_signal.emit("File listing complete")
        self.data_signal.emit(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Forensic Analysis')
        self.setGeometry(100, 100, 1200, 600)  # Adjusted width for more columns

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.textChanged.connect(self.filter_table)

        # Table setup
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)  # Updated to 7 columns
        self.table.setHorizontalHeaderLabels(['Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.table.setSortingEnabled(True)  # Enable sorting

        # Load data button
        self.load_data_button = QPushButton('Load Data', self)
        self.load_data_button.clicked.connect(self.load_data)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.load_data_button)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.thread = WorkerThread(directory)
            self.thread.progress_signal.connect(self.update_status)
            self.thread.data_signal.connect(self.update_table)
            self.thread.start()

    def update_status(self, message):
        print(message)  # For debugging, replace with a status display if needed

    def update_table(self, files):
        self.table.setRowCount(len(files))
        for row, file_info in enumerate(files):
            self.table.setItem(row, 0, QTableWidgetItem(file_info['path']))
            self.table.setItem(row, 1, QTableWidgetItem(file_info['modified_time']))
            self.table.setItem(row, 2, QTableWidgetItem(file_info['created_time']))
            self.table.setItem(row, 3, QTableWidgetItem(file_info['access_time']))
            self.table.setItem(row, 4, QTableWidgetItem(str(file_info['size'])))
            self.table.setItem(row, 5, QTableWidgetItem(file_info['sha256']))
            self.table.setItem(row, 6, QTableWidgetItem('Yes' if file_info['is_suspicious'] else 'No'))

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # Search in the 'Path' column
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
