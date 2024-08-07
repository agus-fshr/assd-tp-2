from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QDialog, QProgressBar, QDesktopWidget
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.widgets.CardWidgets import CardWidget, CardListWidget

from frontend.widgets.MidiNotesViewerWidget import MidiNotesViewerWidget
       

class TracksPage(BaseClassPage):

    title = "Track"    

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.availableMIDIs = QLabel("Available MIDI files: 0")
        self.dropDown = DropDownMenu("Select MIDI File", onChoose=self.on_midi_selected)
        self.trackList = CardListWidget()

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.availableMIDIs)
        topHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addWidget(self.trackList)


    # Refresh dropdown options looking for newly imported MIDI files
    def refresh_midi_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("mid"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)
        self.availableMIDIs.setText(f"Available MIDI files: {len(options)}")

    # Callback for when a MIDI file is selected from the dropdown
    def on_midi_selected(self, name, path):
        midi_data = self.model.midi_handler.parseMidiNotes(path)

        self.trackList.clear()
        
        for channel in midi_data.channels():
            channelData = midi_data.getChannelData(channel)

            title = channelData["title"]
            duration = channelData["duration"]

            subtitle = f"Duration: {duration:.02f}s\n"

            notes = channelData["notes"]


            midiNotesView = MidiNotesViewerWidget(title, self.model, notes)
            # midiNotesView.clicked.connect(synthPopup.exec)

            midiNotesView.plotNotes(notes)

            card = CardWidget(title=title, subtitle=subtitle, child=midiNotesView)
            self.trackList.addCard(card)


    # Refresh dropdown options looking for new MIDI files
    def on_tab_focus(self):
        self.refresh_midi_options()