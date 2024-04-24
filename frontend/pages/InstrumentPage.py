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

        self.noteSlider = Slider(label="Note", range=(0, 127), step=1, minWidth=250)
        self.velocitySlider = Slider(label="Velocity", range=(0, 127), step=1, minWidth=250)

        self.durationSlider = Slider(label="Duration (ms)", range=(10, 2000), step=10, minWidth=250)
        self.velocityOffSlider = Slider(label="Off Velocity", range=(0, 127), step=1, minWidth=250)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        onLayout = QHBoxLayout()
        offLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addStretch(1)

        # Setup controls layout
        onLayout.addWidget(self.noteSlider)
        onLayout.addSpacing(20)
        onLayout.addWidget(self.velocitySlider)
        onLayout.addSpacing(20)
        onLayout.addWidget(Button("Play Note", on_click=self.play_note))
        onLayout.addStretch(1)
        
        offLayout.addWidget(self.durationSlider)
        offLayout.addSpacing(20)
        offLayout.addWidget(self.velocityOffSlider)
        offLayout.addStretch(1)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addLayout(onLayout)
        layout.addLayout(offLayout)

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