from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.PageBaseClass import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider

class ExamplePage(PageBaseClass):
    def __init__(self):
        super().__init__()
        self.title = "Example Page"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.statusLabel = QLabel("Nothing to report")
        self.consoleOutput = QLabel("Console output will appear here")
        self.textA = TextInput(label="Input A", regex="[0-9\-\.]*", on_change=self.on_input)
        self.sliderB = Slider(label="Input B", range=(0, 100), step=1, on_change=self.on_input)

        # Local widgets (used only in the initUI method)
        scrollArea = QScrollArea()
        topHLayout = QHBoxLayout()
        botHLayout = QHBoxLayout()

        # Set scroll area properties
        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scrollArea.setWidget(self.consoleOutput)
        scrollArea.setWidgetResizable(True)

        # Setup top layout
        topHLayout.addWidget(self.textA)
        topHLayout.addWidget(self.sliderB)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.statusLabel)
        topHLayout.addStretch(1) # Add a stretch object

        # Setup bottom layout
        botHLayout.addStretch(1)
        botHLayout.addWidget(Button("Show DataModel", on_click=self.show_data_model))
        botHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addWidget(QLabel("This is an example page."))
        layout.addLayout(topHLayout)
        layout.addWidget(Button("Click Me", on_click=self.on_click))
        layout.addLayout(botHLayout)
        layout.addWidget(scrollArea)

    # input callback
    def on_input(self, dataInput):
        self.statusLabel.setText(f"Some input changed to '{dataInput}'")

    # Sumar A+B
    def on_click(self):
        try:
            a = float(self.textA.text())
            b = self.sliderB.value()
            self.statusLabel.setText(f"Button clicked, A+B={a+b:.2f}")
        except ValueError as e:
            self.statusLabel.setText(f"Error: {e}")
            QMessageBox.critical(self, 'Error', str(e)) # Show a dialog with the error

    # Printear el data model
    def show_data_model(self):
        modelStr = str(self.model) + "\n" + str(self.model.__dict__)
        self.consoleOutput.setText(modelStr)


    def on_tab_focus(self):
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")