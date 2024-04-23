from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.PageBaseClass import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

class ExamplePage(PageBaseClass):
    def __init__(self):
        super().__init__()
        self.title = "Example Page"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.statusLabel = QLabel("Nothing to report")
        self.consoleOutput = ConsoleWidget()
        self.dropDown = DropDownMenu("Select MIDI File", showSelected=False)
        self.textA = TextInput(label="Input A", regex="[0-9\-\.]*", on_change=self.on_input)
        self.sliderB = Slider(label="Input B", range=(0, 100), step=1, on_change=self.on_input)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        botHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.textA)
        topHLayout.addWidget(self.sliderB)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.statusLabel)
        topHLayout.addStretch(1) # Add a stretch object

        # Setup bottom layout
        botHLayout.addWidget(self.dropDown)
        botHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addWidget(QLabel("This is an example page."))
        layout.addLayout(topHLayout)
        layout.addWidget(Button("Click Me", on_click=self.on_click))
        layout.addSpacing(20)
        layout.addLayout(botHLayout)
        layout.addWidget(self.consoleOutput)

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


    def refresh_midi_options(self):
        options = {}
        
        for name in self.model.midi_objects.keys():
            options[name] = lambda k: self.on_midi_selected(k)
            # raise Exception("Error: siempre esta llamando la ultima opcion de la lista de opciones")
        
        self.dropDown.set_options(options)
        self.availableMIDIs.setText(f"Available MIDI files: {len(options)}")

    def on_midi_selected(self, name):
        midi_meta = str(self.model.midi_objects[name].__dict__)
        self.consoleOutput.setText(midi_meta)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")