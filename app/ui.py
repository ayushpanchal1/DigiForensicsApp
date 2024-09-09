from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import pyqtSignal, QThread
from forensic import ForensicAnalyzer
from bin2png import convert_file_to_image
from PyQt5.QtGui import QImage
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

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
        self.analyze_suspicious_files_button = QPushButton("Analyze Suspicious Files")
        self.file_table = QTableWidget()

        # Layout setup
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.load_data_button)
        self.layout.addWidget(self.analyze_suspicious_files_button)
        self.layout.addWidget(self.file_table)
        self.setLayout(self.layout)

        self.file_table.setColumnCount(8)  # Updated to include checkbox column
        self.file_table.setHorizontalHeaderLabels(['Select', 'Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])
        self.file_table.setSortingEnabled(True)  # Enable sorting

        # Connect progress messages to the main window
        self.load_data_button.clicked.connect(self.handle_load_data)
        self.analyze_suspicious_files_button.clicked.connect(self.analyze_suspicious_files)

    def handle_load_data(self):
        self.worker_progress_signal.emit("Button clicked: Starting data load")

    def handle_search(self, text):
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 1)  # Search in the 'Path' column
            if item and text.lower() in item.text().lower():
                self.file_table.setRowHidden(row, False)
            else:
                self.file_table.setRowHidden(row, True)

    def update_file_table(self, file_list):
        self.file_table.setRowCount(len(file_list))
        self.file_table.setColumnCount(8)  # Update column count
        self.file_table.setHorizontalHeaderLabels(['Select', 'Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])

        for row, file in enumerate(file_list):
            checkbox = QCheckBox()
            self.file_table.setCellWidget(row, 0, checkbox)
            self.file_table.setItem(row, 1, QTableWidgetItem(file['path']))
            self.file_table.setItem(row, 2, QTableWidgetItem(str(file['size'])))
            self.file_table.setItem(row, 3, QTableWidgetItem(file['modified_time']))
            self.file_table.setItem(row, 4, QTableWidgetItem(file['created_time']))
            self.file_table.setItem(row, 5, QTableWidgetItem(file['access_time']))
            self.file_table.setItem(row, 6, QTableWidgetItem(file['sha256']))
            self.file_table.setItem(row, 7, QTableWidgetItem('Yes' if file['is_suspicious'] else 'No'))

    def analyze_suspicious_files(self):
        selected_files = []
        for row in range(self.file_table.rowCount()):
            checkbox = self.file_table.cellWidget(row, 0)  # Get checkbox from the 'Select' column
            if checkbox and checkbox.isChecked():
                path = self.file_table.item(row, 1).text()  # Get file path
                selected_files.append({'path': path, 'is_suspicious': True})

        if not selected_files:
            QMessageBox.information(self, "No Files Selected", "No files selected for further analysis.")
            return

        print(f"Selected files for analysis: {selected_files}")  # Debugging line

        self.analyze_thread = AnalyzeThread(selected_files)
        self.analyze_thread.data_signal.connect(self.show_analysis_results)
        self.analyze_thread.start()

    def show_analysis_results(self, results):
        print(f"Analysis results received: {results}")  # Debugging line
        # Implement further actions to display results in the UI

class AnalyzeThread(QThread):
    data_signal = pyqtSignal(list)

    def __init__(self, files):
        super().__init__()
        self.files = files
        self.analyzer = ForensicAnalyzer()

    def run(self):
        results = []
        for file_info in self.files:
            try:
                # Convert the binary file to an image
                img_path = convert_file_to_image(file_info['path'])
                
                # Load and preprocess image for CNN model
                img = image.load_img(img_path, target_size=(128, 128))  # Ensure target_size matches your model input size
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize

                # Predict using CNN model
                prediction = self.analyzer.model.predict(img_array)
                predicted_class = np.argmax(prediction, axis=1)[0]
                is_suspicious = self.analyzer.class_labels[predicted_class]
                results.append((file_info['path'], is_suspicious))
            except Exception as e:
                results.append((file_info['path'], f"Error: {e}"))
        print(f"Analysis results: {results}")  # Debugging line
        self.data_signal.emit(results)
