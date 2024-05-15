from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QFileDialog
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget
from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

import numpy as np
import os
import webbrowser

class MIDIPlayerPage(BaseClassPage):
    
    title = "MIDI Player"

    def initUI(self, layout):
        self.synthSelector = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=self.on_effect_selected)
        self.load_instrument_options()
        self.load_effect_options()

        self.timeLimiter = NumberInput("Time Limit [s]", interval=(0, 100), step=1, default=20)
        self.volume = NumberInput("Volume", interval=(0, 1), step=0.01, default=0.2)

        self.midiSelector = DropDownMenu("Select MIDI File", onChoose=self.on_midi_selected)
        # self.trackSelector = DropDownMenu("Select Track", onChoose=self.on_track_selected)

        synthButton = Button("Synthesize", on_click=lambda: None, background_color="lightblue", hover_color="white")
        synthButton.setFixedWidth(100)

        saveWAVButton = Button("Save WAV", on_click=self.saveWAV)
        openFileExplorerButton = Button("Open Folder", on_click=self.openFileExplorer)

        self.dynamicSettings = DynamicSettingsWidget()
        self.on_instrument_selected(self.model.synthesizers[0].name, self.model.synthesizers[0])

        # Setup audio player widget
        self.player = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Set waveform plotter
        self.waveformViewer = WaveformViewerWidget(navHeight=100)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        controlsHLayout = QHBoxLayout()
        bottomHLayout = QHBoxLayout()
        leftVLayout = QVBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.synthSelector)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.effectSelector)
        topHLayout.addStretch(1)
        topHLayout.addWidget(self.midiSelector)
        # topHLayout.addWidget(self.trackSelector)

        # Setup controls layout
        controlsHLayout.addWidget(self.timeLimiter)
        controlsHLayout.addWidget(self.volume)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(synthButton)


        controlsHLayout.addStretch()
        controlsHLayout.addWidget(saveWAVButton)
        controlsHLayout.addWidget(openFileExplorerButton)
        
        # Setup settings layout
        leftVLayout.addWidget(self.dynamicSettings)
        vplotlay = QVBoxLayout()
        vplotlay.addWidget(self.player)
        vplotlay.addWidget(self.waveformViewer)
        bottomHLayout.addLayout(leftVLayout)
        bottomHLayout.addLayout(vplotlay)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addLayout(controlsHLayout)
        layout.addLayout(bottomHLayout)

    def openFileExplorer(self):
        current_directory = os.getcwd()
        webbrowser.open(current_directory)

    def saveWAV(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        default_filename = self.synthSelector.selected.name + "_out.wav"
        filename, _ = QFileDialog.getSaveFileName(self, "Save as WAV", default_filename, "WAV Files (*.wav)", options=options)
        if filename:
            self.model.audioPlayer.save_to_file(filename)



    def on_song_synthesized(self):
        # set time axis
        time = np.arange(len(self.song_array)) / self.model.audioPlayer.framerate

        self.waveformViewer.plot(time, self.song_array)

        self.model.audioPlayer.set_array(self.song_array)
        self.player.play()

        

    def load_instrument_options(self):
        options = {}
        for synth in self.model.synthesizers:
            options[synth.name] = synth
        self.synthSelector.set_options(options, firstSelected=True)

    def load_effect_options(self):
        options = {}
        for effect in self.model.effects:
            options[effect.name] = effect
        self.effectSelector.set_options(options, firstSelected=True)


    # Display the parameters of the selected effect
    def on_effect_selected(self, name, effect):
        self.dynamicSettings.updateUI(effect.params, title=f"{name} Settings")


    # Display the parameters of the selected instrument
    def on_instrument_selected(self, name, instrument):
        self.dynamicSettings.updateUI(instrument.params, title=f"{name} Settings")




    # Refresh dropdown options looking for newly imported MIDI files
    def refresh_midi_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("mid"):
            options[fmeta.name] = fmeta.path
        
        self.midiSelector.set_options(options)



    # Callback for when a MIDI file is selected from the dropdown
    def on_midi_selected(self, name, path):
        midi_data = self.model.midi_handler.parseMidiNotes(path)

        options = {}

        # self.trackSelector.selected = None
        # self.trackSelector.selected_title = None

        for chKey in midi_data.channels():
            channelData = midi_data.getChannelData(chKey)

            title = channelData["title"]
            
            options[title] = channelData

        # self.trackSelector.set_options(options)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()