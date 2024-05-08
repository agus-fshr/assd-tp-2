from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, SwitchButton, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget

class MidiViewerPage(BaseClassPage):
    
    title = "MIDI Viewer"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.consoleOutput = ConsoleWidget()
        
        self.midiSelector = DropDownMenu("Select MIDI File", onChoose=self.on_midi_selected)
        self.midiDataMenu = DropDownMenu(options=["RAW", "Notes", "NotesPerPitch"], firstSelected=True, onChoose=self.on_midi_selected)
        
        self.filterByOptions = ["All Types"]
        self.filterBySelector = DropDownMenu(onChoose=self.on_midi_selected, options=self.filterByOptions, firstSelected=True)
        self.filterBySelector.hide()

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        botHLayout = QHBoxLayout()


        # Setup bottom layout
        botHLayout.addWidget(self.midiSelector)
        botHLayout.addWidget(self.midiDataMenu)
        botHLayout.addSpacing(20)
        botHLayout.addWidget(self.filterBySelector)
        botHLayout.addStretch(1)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addLayout(botHLayout)
        layout.addWidget(self.consoleOutput)



    # Refresh dropdown options looking for newly imported MIDI files
    def refresh_midi_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("mid"):
            options[fmeta.name] = fmeta.path
        
        self.midiSelector.set_options(options)


    # Callback for when a MIDI file is selected from the dropdown
    def on_midi_selected(self, k, _=None):
        path = self.midiSelector.selected
        if path is None or path == "":
            return

        self.consoleOutput.clear()


        outText = ""
        if self.midiDataMenu.selected == "RAW":
            midi = self.model.midi_handler.get(path)

            self.filterByOptions = ["All Types", "note"]
            self.filterBySelector.show()
            outText += "Internal MIDI data:\n"
            
            cumTime = 0
            for msg in midi:
                if hasattr(msg, 'time'):
                    cumTime += msg.time

                if msg.type not in self.filterByOptions:
                    self.filterByOptions.append(msg.type)

                if self.filterBySelector.selected == "All Types" or self.filterBySelector.selected == msg.type:
                    outText += f"{cumTime:.03f}".ljust(8) + f" {msg.__dict__}\n"

                if self.filterBySelector.selected == "note" and (msg.type == 'note_on' or msg.type == 'note_off'):
                    outText += f"{cumTime:.03f}".ljust(8) + f" {msg.__dict__}\n"

            self.filterBySelector.set_options(self.filterByOptions)



        elif self.midiDataMenu.selected == "Notes":

            midi_data = self.model.midi_handler.parseMidiNotes(path)

            self.filterByOptions = ["All Types"]
            self.filterBySelector.show()

            for channel in midi_data.channels():

                channel_str = f"CHANNEL {channel}"
                
                if channel_str not in self.filterByOptions:
                    self.filterByOptions.append(channel_str)

                if self.filterBySelector.selected == "All Types" or self.filterBySelector.selected == channel_str:
                    outText += channel_str + "\n"
   
                    channel_notes = midi_data.getChannelNotes(channel)
                    
                    for note in channel_notes:
                        outText += "\t" + str(note) + "\n"

            # order options
            self.filterByOptions.sort(key=lambda x: x.split(" ")[1])
            self.filterBySelector.set_options(self.filterByOptions)


        elif self.midiDataMenu.selected == "NotesPerPitch":

            midi_data = self.model.midi_handler.parseMidiNotes(path)

            self.filterByOptions = ["All Types"]
            self.filterBySelector.show()

            for channel in midi_data.channels():
                outText += f"CHANNEL {channel}\n"
                channel_notes = midi_data.getChannelRawNotes(channel)
                
                for nkey in channel_notes:
                    note_str = f"NOTE {nkey}"
                    if note_str not in self.filterByOptions:
                        self.filterByOptions.append(note_str)

                    if self.filterBySelector.selected == "All Types" or self.filterBySelector.selected == note_str:
                        outText += "\t " + note_str + " \n"

                        for note in channel_notes[nkey]:
                            outText += "\t\t" + str(note) + "\n"
            # order options
            self.filterByOptions.sort(key=lambda x: x.split(" ")[1])
            self.filterBySelector.set_options(self.filterByOptions)

        self.consoleOutput.setText(outText)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()