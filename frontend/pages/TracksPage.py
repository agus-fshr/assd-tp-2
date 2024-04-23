from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.PageBaseClass import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.views.CardViews import CardViewWidget, CardListWidget

class TracksPage(PageBaseClass):
    def __init__(self):
        super().__init__()
        self.title = "Tracks"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.availableMIDIs = QLabel("Available MIDI files: 0")
        self.dropDown = DropDownMenu("Select MIDI File", showSelected=False)
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


    def refresh_midi_options(self):
        options = {}
        
        for name in self.model.midi_objects.keys():
            options[name] = lambda k: self.on_midi_selected(k)
            # raise Exception("Error: siempre esta llamando la ultima opcion de la lista de opciones")
        
        self.dropDown.set_options(options)
        self.availableMIDIs.setText(f"Available MIDI files: {len(options)}")

    def on_midi_selected(self, name):
        midi_meta = self.model.get_midi_metadata(name)
        self.trackList.clear()
        for trackMeta in midi_meta["trackMeta"]:
            childTextData = f"Port: {trackMeta['port']}     " if "port" in trackMeta else ""
            childTextData += f"Channel: {trackMeta['channel_prefix']}\n" if 'channel_prefix' in trackMeta else ""
            childTextData += f"Ref. Channels: {trackMeta['refChannels']}        {trackMeta['ticks']}" if 'refChannels' in trackMeta else ""
            card = CardViewWidget(child=QLabel(childTextData), mainTitle=trackMeta["name"])     # Esta medio confuso el uso de "name"
            self.trackList.addCard(card)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")