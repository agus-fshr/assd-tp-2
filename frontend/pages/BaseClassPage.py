import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

# DO NOT MODIFY THIS CLASS
class BaseClassPage(QWidget):

    # DO NOT MODIFY THIS CLASS
    def __init__(self):
        super().__init__()
        self.model = None
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        if not hasattr(self, 'title'):
            raise Exception("All pages must have a title attribute")
    
    # DO NOT MODIFY THIS CLASS
    def initUI(self, layout):
        raise NotImplementedError("initUI(self, layout) must be implemented in Page class")

    def set_model(self, model):
        self.model = model

    def on_tab_focus(self):
        pass

    def on_tab_unfocus(self):
        pass