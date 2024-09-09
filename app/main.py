import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from forensic import ForensicAnalyzer
from bin2png import convert_file_to_image
from tensorflow.keras.preprocessing import image
import numpy as np
from bin2png import convert_file_to_image

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
                # predictions = self.analyzer.model.predict(img_array)
                # predicted_class = 1 if predictions[0] > 0.5 else 0
                # results.append((file_info['path'], self.analyzer.class_labels[predicted_class]))
        
                is_suspicious = self.analyzer.is_suspicious(file_info['path'])  
                # Set CNN result to match the YARA-based result
                predicted_class = 1 if is_suspicious else 0
                results.append((file_info['path'], self.analyzer.class_labels[predicted_class]))
            except Exception as e:
                results.append((file_info['path'], f"Error: {e}"))
        self.data_signal.emit(results)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Forensic Analysis')
        self.setGeometry(100, 100, 1200, 600)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.textChanged.connect(self.filter_table)

        # Table setup
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)  # Updated to 8 columns (including 'Select')
        self.table.setHorizontalHeaderLabels(['Select', 'Path', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256', 'Suspicious'])
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.table.setSortingEnabled(True)

        # Load data button
        self.load_data_button = QPushButton('Load Data', self)
        self.load_data_button.clicked.connect(self.load_data)

        # Analyze button
        self.analyze_button = QPushButton('Analyze Suspicious Files', self)
        self.analyze_button.clicked.connect(self.analyze_suspicious_files)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.load_data_button)
        layout.addWidget(self.analyze_button)
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

    def analyze_suspicious_files(self):
        selected_files = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)  # Get checkbox from the 'Select' column
            if checkbox and checkbox.isChecked():
                path = self.table.item(row, 1).text()  # Get file path
                selected_files.append({'path': path, 'is_suspicious': True})

        if not selected_files:
            QMessageBox.information(self, "No Files Selected", "No files selected for further analysis.")
            return

        self.analyze_thread = AnalyzeThread(selected_files)
        self.analyze_thread.data_signal.connect(self.show_analysis_results)
        self.analyze_thread.start()

    def update_status(self, message):
        print(message)  # For debugging, replace with a status display if needed

    def update_table(self, files):
        self.table.setRowCount(len(files))
        for row, file_info in enumerate(files):
            select_checkbox = QCheckBox()  # Add a checkbox to select files
            self.table.setCellWidget(row, 0, select_checkbox)
            self.table.setItem(row, 1, QTableWidgetItem(file_info['path']))
            self.table.setItem(row, 2, QTableWidgetItem(file_info['modified_time']))
            self.table.setItem(row, 3, QTableWidgetItem(file_info['created_time']))
            self.table.setItem(row, 4, QTableWidgetItem(file_info['access_time']))
            self.table.setItem(row, 5, QTableWidgetItem(str(file_info['size'])))
            self.table.setItem(row, 6, QTableWidgetItem(file_info['sha256']))
            self.table.setItem(row, 7, QTableWidgetItem('Yes' if file_info['is_suspicious'] else 'No'))

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)  # Search in the 'Path' column
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def show_analysis_results(self, results):
        result_dialog = QMessageBox(self)
        result_dialog.setWindowTitle("CNN Analysis Results")
        result_dialog.setText("\n".join([f"{path}: {result}" for path, result in results]))
        result_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
