from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider, QFileDialog
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget

from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

import numpy as np
from scipy import signal
import csv
from itertools import islice


class SoundPlayerPage(BaseClassPage):

    title = "Sound Player"    

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Sound", onChoose=self.on_sound_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        importCSVButton = Button("Import CSV", on_click=self.on_import_csv)

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addSpacing(20)
        topHLayout.addWidget(importCSVButton)
        topHLayout.addStretch(1)

        # Setup audio player widget
        self.playerWidget = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Setup waveform viewer widget
        self.plotWidget = WaveformViewerWidget()
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addWidget(self.playerWidget)
        layout.addSpacing(20)
        layout.addWidget(self.plotWidget)


    def on_import_csv(self):
        # Open file dialog
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setNameFilter("CSV Files (*.csv)")
        time_array = None
        channel2_array = None
        if fileDialog.exec_():
            fileNames = fileDialog.selectedFiles()
            for fileName in fileNames:
                with open(fileName, 'r') as csv_file:
                    lines = csv_file.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith("Time"):
                            break
                    csv_reader = csv.reader(lines[i:])
                    header = next(csv_reader)
                    time_index = header.index('Time (s)')
                    channel2_index = header.index('Channel 2 (V)')
                    time_data = []
                    channel2_data = []
                    for row in csv_reader:
                        time_data.append(float(row[time_index]))
                        channel2_data.append(float(row[channel2_index]))
                    time_array = np.array(time_data)
                    channel2_array = np.array(channel2_data)
        if time_array is not None and channel2_array is not None:
            time_array = time_array - time_array[0]
            channel2_array = (channel2_array - np.mean(channel2_array)) * 0.8
            self.plotWidget.plot(time_array, channel2_array)

            # convert time_array and channel2_array (floats) to valid 44100 Hz audio
            # time_array is in seconds
            channel2_array = signal.resample(channel2_array, int(time_array[-1] * 44100))
            self.model.audioPlayer.set_array(channel2_array)


    # Refresh dropdown options looking for newly imported .WAV files
    def refresh_sound_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("wav"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)


    # Callback to set the selected sound to play
    def on_sound_selected(self, name, path):
        self.model.audioPlayer.set_from_file(path)

        time, array = self.model.audioPlayer.get_numpy_data()

        self.plotWidget.plot(time, array)


    # Refresh dropdown options looking for new sound files
    def on_tab_focus(self):
        self.refresh_sound_options()
