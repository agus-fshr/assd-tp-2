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

class InstrumentPage(BaseClassPage):
    
    title = "Instrument Testbench"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.synthSelector = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=self.on_effect_selected)
        self.load_instrument_options()
        self.load_effect_options()

        self.midiNoteSelector = NumberInput("Note", default=69, interval=(0, 127), step=1)
        self.ampSelector = NumberInput("Amplitude", default=0.5, interval=(0, 1), step=0.01)
        self.durationSelector = NumberInput("Duration", default=0.4, interval=(0, 3), step=0.1)
        
        synthButton = Button("Synthesize", on_click=self.synthesize, background_color="lightgreen", hover_color="white")
        synthButton.setFixedWidth(150)
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
        settingsHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.synthSelector)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.effectSelector)
        topHLayout.addStretch(1)

        # Setup controls layout
        controlsHLayout.addWidget(self.midiNoteSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(self.ampSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(self.durationSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(synthButton)
        controlsHLayout.addSpacing(10)
        controlsHLayout.addWidget(saveWAVButton)
        controlsHLayout.addWidget(openFileExplorerButton)
        
        # Setup settings layout
        settingsHLayout.addWidget(self.dynamicSettings)
        vplotlay = QVBoxLayout()
        vplotlay.addWidget(self.player)
        vplotlay.addWidget(self.waveformViewer)
        settingsHLayout.addLayout(vplotlay)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addLayout(controlsHLayout)
        layout.addLayout(settingsHLayout)

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


    # Synthesize a sound using the selected instrument and effect
    def synthesize(self):
        note = self.midiNoteSelector.value()
        amp = self.ampSelector.value()
        duration = self.durationSelector.value()

        instrument = self.synthSelector.selected
        effect = self.effectSelector.selected

        wave_array = instrument(note, amp, duration)
        wave_array = effect(wave_array)

        # set time axis
        framerate = self.model.audioPlayer.framerate
        time = np.arange(len(wave_array)) / framerate

        self.waveformViewer.plot(time, wave_array)

        self.model.audioPlayer.set_array(wave_array)
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