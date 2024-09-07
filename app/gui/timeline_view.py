from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class TimelineView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Interactive Timeline View")
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setMinimumSize(400, 300)


# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget

# class TimelineView(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()

#         # Add a list widget to represent timeline events
#         self.timeline_list = QListWidget()
#         self.timeline_list.addItem("Event 1: System Boot")
#         self.timeline_list.addItem("Event 2: User Login")
#         self.timeline_list.addItem("Event 3: Suspicious Activity Detected")

#         layout.addWidget(self.timeline_list)

#         self.setLayout(layout)
#         self.setMinimumSize(400, 300)
