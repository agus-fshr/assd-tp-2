from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget

class SoundPlayerPage(BaseClassPage):
    def __init__(self):
        super().__init__()
        self.title = "Sound Player"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Sound", onChoose=self.on_sound_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addStretch(1)

        # Setup audio player widget
        self.player = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addWidget(self.player)


    def refresh_sound_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("wav"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)

    def on_error(self, error):
        QMessageBox.critical(self, 'Error', str(error))

    def on_sound_selected(self, name, path):
        wave = self.model.wav_handler.get_wave(path)
        self.model.audioPlayer.set_wave_obj(wave)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_sound_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")