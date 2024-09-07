from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from gui.data_visualization import DataVisualization
from gui.timeline_view import TimelineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Triage Tool")
        
        # Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Adding components
        self.data_visualization = DataVisualization()
        self.timeline_view = TimelineView()
        
        layout.addWidget(self.data_visualization)
        layout.addWidget(self.timeline_view)
        
        self.resize(800, 600)
