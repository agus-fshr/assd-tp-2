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

class ChordPage(BaseClassPage):
    
    title = "Chord Testbench"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.noteArr = []

        self.synthSelector = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=self.on_effect_selected)
        self.load_instrument_options()
        self.load_effect_options()

        self.freqSelector = NumberInput("Note", default=69, interval=(0, 127), step=1)
        self.ampSelector = NumberInput("Amplitude", default=0.4, interval=(0, 1), step=0.01)
        self.durationSelector = NumberInput("Duration", default=0.4, interval=(0, 3), step=0.1)
        self.delaySelector = NumberInput("Delay", default=0.2, interval=(0, 5), step=0.01)

        self.noteViewerConsole = ConsoleWidget(fixedWidth=350)

        addButton = Button("Add Note", on_click=self.addNote, background_color="lightgreen", hover_color="white")
        penScaleButton = Button("Pen Scale", on_click=self.penScale, background_color="yellow", hover_color="white")
        popButton = Button("Pop Note", on_click=self.popNote, background_color="lightcoral", hover_color="white")
        synthButton = Button("Synthesize", on_click=self.synthesize, background_color="lightblue", hover_color="white")
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
        bottomHLayout = QHBoxLayout()
        leftVLayout = QVBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.synthSelector)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(self.effectSelector)
        topHLayout.addStretch(1)

        # Setup controls layout
        controlsHLayout.addWidget(self.freqSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(self.ampSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(self.durationSelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(self.delaySelector)
        controlsHLayout.addSpacing(20)
        controlsHLayout.addWidget(synthButton)
        controlsHLayout.addSpacing(10)
        controlsHLayout.addWidget(addButton)
        controlsHLayout.addWidget(popButton)
        controlsHLayout.addWidget(penScaleButton)
        controlsHLayout.addSpacing(10)
        controlsHLayout.addWidget(saveWAVButton)
        controlsHLayout.addWidget(openFileExplorerButton)
        
        # Setup settings layout
        leftVLayout.addWidget(self.noteViewerConsole)
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


    # Synthesize a sound using the selected instrument and effect
    def synthesize(self):

        song_length = 0
        for note in self.noteArr:
            song_length += int(note["Delay"] * self.model.audioPlayer.framerate)
        
        song_length += int(self.noteArr[-1]["Duration"] * self.model.audioPlayer.framerate)

        print(f"Song Length (Samples): {song_length}")
        
        song_array = np.zeros(song_length + self.model.audioPlayer.framerate * 2)

        curr = 0
        for note in self.noteArr:
            freq = note["Note"]
            amp = note["Amplitude"]
            duration = note["Duration"]
            delay = note["Delay"]

            instrument = self.synthSelector.selected
            effect = self.effectSelector.selected
            wave_array = instrument(freq, amp, duration)
            wave_array = effect(wave_array)


            if curr + wave_array.size >= song_array.size:
                song_array[curr:] += wave_array[:song_array.size - curr]
                print("ERROR: Song too short or note too long. Breaking loop.")
                print("song_array size: ", song_array.size)
                print("wave_array size: ", wave_array.size)
                break

            song_array[curr : curr + wave_array.size] += wave_array

            curr += int(delay * self.model.audioPlayer.framerate)


        # set time axis
        time = np.arange(len(song_array)) / self.model.audioPlayer.framerate


        self.waveformViewer.plot(time, song_array)

        self.model.audioPlayer.set_array(song_array)
        self.player.play()

    def updateConsole(self):
        text = "Time     Note\tAmp \tDur\n"
        absTime = 0
        for note in self.noteArr:
            absTime += note["Delay"]
            timestr = f"{absTime:.03f}".ljust(8)
            text += f"{timestr} {note['Note']}\t{note['Amplitude']:.02f}\t{note['Duration']:.03f}\n"
        self.noteViewerConsole.setText(text)

    def popNote(self):
        self.noteArr.pop()
        self.updateConsole()

    def penScale(self):
    #   A minor pentatonic     A4,     C4,     D4,     E4,     G4,    A5
    #   A_minor_pentatonic = [440, 523.25, 587.33, 659.25, 783.99, 880]
        A_minor_pentatonic = ["A4", "C5", "D5", "E5", "G5", "A5"]

        self.noteArr = []

        for noteName in A_minor_pentatonic:
            note = {}
            note["Note"] = noteName
            note["Amplitude"] = self.ampSelector.value()
            note["Duration"] = self.durationSelector.value()
            note["Delay"] = self.delaySelector.value()

            self.noteArr.append(note)
        
        self.noteArr[-1]["Delay"] = 1.5

        for noteName in A_minor_pentatonic:
            note = {}
            note["Note"] = noteName
            note["Amplitude"] = self.ampSelector.value()
            note["Duration"] = 2
            note["Delay"] = 0

            self.noteArr.append(note)

        self.updateConsole()

    def addNote(self):
        print("Note added!")

        note = {}
        note["Note"] = self.freqSelector.value()
        note["Amplitude"] = self.ampSelector.value()
        note["Duration"] = self.durationSelector.value()
        note["Delay"] = self.delaySelector.value()

        self.noteArr.append(note)
        self.updateConsole()
        

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
