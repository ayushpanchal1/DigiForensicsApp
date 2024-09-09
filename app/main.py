from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from forensic import ForensicAnalyzer
from bin2png import convert_file_to_image
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import pandas as pd

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
                is_suspicious = self.analyzer.is_suspicious(file_info['path'])  
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

        # Generate report button
        self.generate_report_button = QPushButton('Generate Report', self)
        self.generate_report_button.clicked.connect(self.generate_report)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.load_data_button)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.generate_report_button)
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

    def generate_report(self):
        files = []
        for row in range(self.table.rowCount()):
            file_info = {
                'path': self.table.item(row, 1).text(),
                'size': int(self.table.item(row, 5).text()),
                'modified_time': self.table.item(row, 2).text(),
                'created_time': self.table.item(row, 3).text(),
                'access_time': self.table.item(row, 4).text(),
                'sha256': self.table.item(row, 6).text(),
                'is_suspicious': self.table.item(row, 7).text() == 'Yes'
            }
            files.append(file_info)
        
        report_path = 'file_report.html'
        self.create_html_report(files, report_path)
        QMessageBox.information(self, "Report Generated", f"Report generated: {report_path}")

    def create_html_report(self, files, report_path):
        file_extension_counts = {}
        duplicate_files = set()
        seen_checksums = set()
        suspicious_count = 0
        
        html = '''
        <html>
        <head>
        <title>File Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #2c3e50;
            }
            h2 {
                color: #34495e;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            ul li {
                margin-bottom: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
                color: #333;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            .summary-section {
                margin-bottom: 20px;
            }
        </style>
        </head>
        <body>
        <h1>File Report</h1>
        <div class="summary-section">
            <h2>Summary</h2>
            <ul>
        '''
        
        # Count file extensions and detect duplicates
        for file in files:
            ext = os.path.splitext(file['path'])[1].lower()
            file_extension_counts[ext] = file_extension_counts.get(ext, 0) + 1
            
            checksum = file['sha256']
            if checksum in seen_checksums:
                duplicate_files.add(file['path'])
            seen_checksums.add(checksum)
            
            if file['is_suspicious']:
                suspicious_count += 1
        
        # Add summary to HTML
        html += f'<li>Total Files: {len(files)}</li>'
        for ext, count in file_extension_counts.items():
            html += f'<li>{count} {ext} files</li>'
        html += f'<li>Suspicious Files: {suspicious_count}</li>'
        html += f'<li>Duplicate Files: {len(duplicate_files)}</li>'
        html += '''
            </ul>
        </div>
        <h2>Detailed File Information</h2>
        <table>
        <tr>
        <th>Path</th>
        <th>Size</th>
        <th>Modified Time</th>
        <th>Created Time</th>
        <th>Access Time</th>
        <th>SHA-256</th>
        <th>Suspicious</th>
        </tr>
        '''
        
        # Add detailed file information to HTML
        for file in files:
            html += f'''
            <tr>
            <td>{file['path']}</td>
            <td>{file['size']}</td>
            <td>{file['modified_time']}</td>
            <td>{file['created_time']}</td>
            <td>{file['access_time']}</td>
            <td>{file['sha256']}</td>
            <td>{'Yes' if file['is_suspicious'] else 'No'}</td>
            </tr>
            '''
        
        html += '''
        </table>
        </body>
        </html>
        '''
        
        # Save the report to file
        with open(report_path, 'w') as f:
            f.write(html)


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

    def show_analysis_results(self, results):
        # This method should display the results of the analysis
        result_dialog = QMessageBox(self)
        result_dialog.setWindowTitle("CNN Analysis Results")
        result_dialog.setText("\n".join([f"{path}: {result}" for path, result in results]))
        result_dialog.exec_()
        pass

    def filter_table(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and text.lower() in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
