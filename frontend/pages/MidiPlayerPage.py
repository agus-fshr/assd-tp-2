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
        self.trackSelector = DropDownMenu("Select Track", onChoose=self.on_track_selected)

        synthButton = Button("Synthesize", on_click=self.synthesize, background_color="lightblue", hover_color="white")
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
        topHLayout.addWidget(self.trackSelector)

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


    # Synthesize a sound using the selected instrument and effect
    def synthesize(self):

        self.song_length = 0
        for note in self.noteArr:
            self.song_length += int(note["Delay"]*1.01 * self.model.audioPlayer.framerate)
        
        self.song_length += int(self.noteArr[-1]["Duration"] * self.model.audioPlayer.framerate)

        print(f"Song Length (Samples): {self.song_length}")
        
        self.song_array = np.zeros(self.song_length + self.model.audioPlayer.framerate * 1)

        self.model.synthWorker.cancel()
        self.model.synthWorker.wait()

        n0 = 0
        for i, note in enumerate(self.noteArr):
            freq = note["Frequency"]
            amp = note["Amplitude"]
            duration = note["Duration"]
            delay = note["Delay"]

            instrument = self.synthSelector.selected
            effect = self.effectSelector.selected

            n0 += int(delay * self.model.audioPlayer.framerate)
            self.model.synthWorker.add_task((n0, note, instrument, effect))

        self.model.synthWorker.disconnectAll()
        self.model.synthWorker.taskComplete.connect(self.on_note_synthesized)
        self.model.synthWorker.finished.connect(self.on_song_synthesized)
        self.model.synthWorker.onError.connect( lambda e: print(f"Synth Worker Error: {e}"))

        self.model.synthWorker.start()


    def on_note_synthesized(self, n0_wave):
        n0, wave_array = n0_wave
        try:
            if n0 + wave_array.size >= self.song_array.size:
                print("ERROR: Song too short or note too long. Breaking loop.")
                print("song_array size: ", self.song_array.size)
                print("wave_array size: ", wave_array.size)
                self.song_array[n0:] += wave_array[:self.song_array.size - n0]
                self.model.synthWorker.cancel()
                return

            self.song_array[n0 : n0 + wave_array.size] += wave_array
            print(self.model.synthWorker.progressBarString())
        except Exception as e:
            print(e)
            self.model.synthWorker.cancel()
            self.model.synthWorker.wait()
            return


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


    def on_track_selected(self, name, channelData):
        self.noteArr = []

        notes = channelData["notes"]

        lastTime = 0.0

        for n in notes:
            f = 440 * 2**((n.note - 69) / 12)
            d = n.time_on - lastTime
            lastTime = n.time_on

            if n.time_off is not None and n.time_off > self.timeLimiter.value():
                print("Reached time limit!")
                break

            note = {}
            note["Frequency"] = f
            note["Amplitude"] = (n.velocity / 127) * self.volume.value()
            note["Duration"] = n.duration
            note["Delay"] = d

            self.noteArr.append(note)
            print(f"Note added! n={n.note}, f={f:.0f}, t0 ={n.time_on:.02f}, t1={n.time_off:.02f}, d = {d:.02f}")



    # Callback for when a MIDI file is selected from the dropdown
    def on_midi_selected(self, name, path):
        midi_data = self.model.midi_handler.parseMidiNotes(path)

        options = {}

        self.trackSelector.selected = None
        self.trackSelector.selected_title = None

        for chKey in midi_data.channels():
            channelData = midi_data.getChannelData(chKey)

            title = channelData["title"]
            
            options[title] = channelData

        self.trackSelector.set_options(options)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_midi_options()