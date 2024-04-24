from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

class InstrumentPage(BaseClassPage):
    def __init__(self):
        super().__init__()
        self.title = "Instrument Testbench"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)

        self.noteSlider = Slider(label="Note", range=(0, 127), step=1, minWidth=200)
        self.velocitySlider = Slider(label="Velocity", range=(0, 127), step=1, minWidth=200)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.noteSlider)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.velocitySlider)
        topHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addLayout(self.dropDown)
        layout.addSpacing(20)
        layout.addLayout(topHLayout)
        layout.addWidget(Button("Play Note", on_click=self.play_note))

    # Play the selected note
    def play_note(self):
        note = self.noteSlider.value()
        velocity = self.velocitySlider.value()


    def refresh_instrument_options(self):
        pass        
        # options = {}
        # self.dropDown.set_options(options)


    # Callback for when a MIDI file is selected from the dropdown
    def on_instrument_selected(self, key, val):
        pass


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_instrument_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")