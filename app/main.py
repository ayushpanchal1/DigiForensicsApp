import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from ui_mainwindow import Ui_MainWindow
from analysis import extract, registry, logs, network, timestamp, malware, report

class ForensicAnalysisThread(QThread):
    update_progress = pyqtSignal(int)
    analysis_done = pyqtSignal(dict)

    def __init__(self, analysis_type, image_path, output_dir):
        super().__init__()
        self.analysis_type = analysis_type
        self.image_path = image_path
        self.output_dir = output_dir

    def run(self):
        results = {}
        # Run the specific analysis based on the analysis type
        if self.analysis_type == 'extract':
            extract.extract_files(self.image_path, self.output_dir)
            results['extract'] = "Files extracted successfully."
        elif self.analysis_type == 'registry':
            results['registry'] = registry.extract_registry_entries(self.image_path)
        elif self.analysis_type == 'logs':
            results['logs'] = logs.extract_system_logs(self.image_path)
        elif self.analysis_type == 'network':
            results['network'] = network.analyze_network_traffic(self.image_path)
        elif self.analysis_type == 'timestamp':
            results['timestamp'] = timestamp.print_file_timestamps(self.image_path)
        elif self.analysis_type == 'malware':
            results['malware'] = malware.scan_file_for_yara(self.image_path)
        
        self.analysis_done.emit(results)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connect_signals()

    def connect_signals(self):
        self.pushButtonStartAnalysis.clicked.connect(self.start_analysis)
        self.pushButtonGenerateReport.clicked.connect(self.generate_report)
    
    def start_analysis(self):
        # File dialog for selecting forensic image
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Forensic Image")
        if not image_path:
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        # Determine which tab is selected for analysis type
        analysis_type = self.tabWidget.currentWidget().objectName()

        # Start the analysis in a separate thread
        self.analysis_thread = ForensicAnalysisThread(analysis_type, image_path, output_dir)
        self.analysis_thread.update_progress.connect(self.update_progress)
        self.analysis_thread.analysis_done.connect(self.display_results)
        self.analysis_thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def display_results(self, results):
        # Display results in the appropriate widget (e.g., QTextBrowser)
        if 'extract' in results:
            self.textBrowserResults.setText(results['extract'])
        elif 'registry' in results:
            self.textBrowserResults.setText(results['registry'])
        # Handle other types similarly...
        
        QMessageBox.information(self, "Analysis Complete", "The analysis is complete.")
    
    def generate_report(self):
        data = {
            'files': [],  # Populate with extracted data
            'registry': [],
            'logs': [],
            'network': [],
            'malware': []
        }
        report.generate_report(data, 'templates/report_template.html', 'forensic_report.pdf')
        QMessageBox.information(self, "Report Generated", "The forensic report has been generated.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
