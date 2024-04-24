from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

class TracksMetadataPage(BaseClassPage):
    def __init__(self):
        super().__init__()
        self.title = "Tracks Metadata"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.consoleOutput = ConsoleWidget()
        self.availableMIDIs = QLabel("Available MIDI files: 0")
        self.dropDown = DropDownMenu("Select MIDI File", onChoose=self.on_midi_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.availableMIDIs)
        topHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addWidget(self.consoleOutput)


    def refresh_midi_options(self):
        options = {}
        for name in self.model.file_handler.available_files():
            options[name] = self.model.file_handler.path(name)
        
        self.dropDown.set_options(options)
        self.availableMIDIs.setText(f"Available MIDI files: {len(options)}")


    def on_midi_selected(self, name, path):
        midi_meta = self.model.midi_handler.get_pretty_midi_metadata_str(path)
        self.consoleOutput.setText(midi_meta)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")