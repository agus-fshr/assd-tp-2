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


class SoundPlayerPage(BaseClassPage):

    title = "Sound Player"    

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Sound", onChoose=self.on_sound_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
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
