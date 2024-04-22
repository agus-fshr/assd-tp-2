import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class PageBaseClass(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "PageBaseClass"
        self.model = None

        # Create a QVBoxLayout to arrange the widgets vertically
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.initUI(layout)
        self.setLayout(layout)
    
    def initUI(self, layout):
        raise NotImplementedError("initUI(self, layout, model) must be implemented in Page subclass")

    def set_model(self, model):
        self.model = model

    def on_tab_focus(self):
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")