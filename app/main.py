import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from ui import MainWindow
from forensic import ForensicAnalyzer

class Worker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        self.progress.emit("Worker thread started")
        analyzer = ForensicAnalyzer()
        self.progress.emit("Starting file listing")
        files = analyzer.list_files(self.directory)
        self.progress.emit("File listing completed")
        self.finished.emit(files)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainWindow(self)
        self.setCentralWidget(self.ui)
        self.ui.load_data_button.clicked.connect(self.load_data)

    def load_data(self):
        self.ui.worker_progress_signal.emit("Loading data...")
        # Replace 'Z:' with the drive letter where the image is mounted
        self.thread = Worker('E:/')
        self.thread.finished.connect(self.update_file_table)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()

    def update_file_table(self, files):
        self.ui.update_file_table(files)
        print("File table updated")

    def update_progress(self, message):
        print(message)  # Print progress messages to the console

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
