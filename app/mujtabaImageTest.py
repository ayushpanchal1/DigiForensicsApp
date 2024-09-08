import sys
import pytsk3
import hashlib
import yara
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from datetime import datetime

class ForensicAnalyzer(QMainWindow):
    def init(self):
        super().init()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Forensic Analyzer")
        self.setGeometry(100, 100, 800, 600)

        self.selectButton = QPushButton('Select Image', self)
        self.selectButton.clicked.connect(self.selectimage)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(['File', 'Modified Time', 'Created Time', 'Access Time', 'Size', 'SHA-256'])

    def select_image(self):
        image_file,  = QFileDialog.getOpenFileName(self, 'Select Forensic Image', '', 'Disk Images (.dd.img)')
        if image_file:
            self.analyze_image(image_file)

    def analyze_image(self, image_file):
        # Disk image extraction logic using pytsk3
        with open(image_file, 'rb') as img:
            # Analyze and extract file metadata
            pass

    def addfiletotable(self, filemetadata):
        # Adding extracted file details to the table
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, QTableWidgetItem(file_metadata['name']))
        self.tableWidget.setItem(row, 1, QTableWidgetItem(file_metadata['modified_time']))
        self.tableWidget.setItem(row, 2, QTableWidgetItem(file_metadata['created_time']))
        self.tableWidget.setItem(row, 3, QTableWidgetItem(file_metadata['access_time']))
        self.tableWidget.setItem(row, 4, QTableWidgetItem(str(file_metadata['size'])))
        self.tableWidget.setItem(row, 5, QTableWidgetItem(file_metadata['sha256_hash']))

    def calculate_sha256(self, file):
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def flag_files_with_yara(self, file):
        # Use yara rules to flag suspicious files
        yara_rules = yara.compile(filepath='rules.yar')
        matches = yara_rules.match(file)
        return matches

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ForensicAnalyzer()
    window.show()
    sys.exit(app.exec_())