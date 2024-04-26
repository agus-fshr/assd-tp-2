from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.widgets.CardWidgets import CardWidget, CardListWidget

class TracksPage(BaseClassPage):

    title = "Tracks"    

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
        midi_meta = self.model.midi_handler.get_midi_metadata(path)
        self.trackList.clear()
        for trackMeta in midi_meta["trackMeta"]:
            childTextData = f"Port: {trackMeta['port']}     " if "port" in trackMeta else ""
            childTextData += f"Channel: {trackMeta['channel_prefix']}\n" if 'channel_prefix' in trackMeta else ""
            childTextData += f"Ref. Channels: {trackMeta['refChannels']}        {trackMeta['ticks']}" if 'refChannels' in trackMeta else ""
            card = CardWidget(child=QLabel(childTextData), mainTitle=trackMeta["name"])
            self.trackList.addCard(card)


    # Refresh dropdown options looking for new MIDI files
    def on_tab_focus(self):
        self.refresh_midi_options()