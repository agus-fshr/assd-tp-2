from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.PageBaseClass import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider

class TracksPage(PageBaseClass):
    def __init__(self):
        super().__init__()
        self.title = "Tracks"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.consoleOutput = QLabel("Console output will appear here")
        self.consoleOutput.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Local widgets (used only in the initUI method)
        scrollArea = QScrollArea()
        topHLayout = QHBoxLayout()

        # Set scroll area properties
        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scrollArea.setWidget(self.consoleOutput)
        scrollArea.setWidgetResizable(True)

        # Setup top layout
        topHLayout.addWidget(Button("Print To Console", on_click=self.print_to_console))

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addWidget(scrollArea)

    # Printear el data model
    def print_to_console(self):
        modelStr = str(self.model) + "\n" + str(self.model.__dict__)
        self.consoleOutput.setText(modelStr)


    def on_tab_focus(self):
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")