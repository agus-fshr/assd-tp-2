from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

class ExamplePage(BaseClassPage):
    def __init__(self):
        super().__init__()
        self.title = "Example Page"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.statusLabel = QLabel("Nothing to report")
        self.consoleOutput = ConsoleWidget()
        self.dropDown = DropDownMenu("Select MIDI File", onChoose=self.on_midi_selected)
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


    # Refresh dropdown options looking for newly imported MIDI files
    def refresh_midi_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("mid"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)


    # Callback for when a MIDI file is selected from the dropdown
    def on_midi_selected(self, name, path):
        midi = self.model.midi_handler.get(path)
        internal = "Internal MIDI data:\n"
        cumTime = 0
        for msg in midi:
            if hasattr(msg, 'time'):
                cumTime += msg.time
            internal += f"{cumTime:.02f}".ljust(8) + f" {msg}\n"
        self.consoleOutput.setText(internal)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")