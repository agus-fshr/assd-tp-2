from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget
from backend.audio.AudioPlayer import AudioPlayer

class SoundPlayerPage(BaseClassPage):
    def __init__(self):
        self.audioPlayer = AudioPlayer()
        super().__init__()  # This initializes initUI, so it must be called after audioPlayer is created
        self.title = "Sound Player"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Sound", onChoose=self.on_sound_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        controlsLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addStretch(1)

        # Setup controls layout
        controlsLayout.addWidget(Button("Play", on_click=self.audioPlayer.play_audio))
        controlsLayout.addWidget(Button("Pause", on_click=self.audioPlayer.pause_audio))
        controlsLayout.addWidget(Button("Stop", on_click=self.audioPlayer.stop_audio))
        controlsLayout.addStretch(1)
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addLayout(controlsLayout)


    def refresh_sound_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("wav"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)


    def on_sound_selected(self, name, path):
        wave = self.model.wav_handler.get_wave(path)
        
        self.audioPlayer.set_wave_obj(wave)


    def on_tab_focus(self):
        # Refresh dropdown options looking for new MIDI files
        self.refresh_sound_options()
        print(f"Page '{self.title}' focused")

    def on_tab_unfocus(self):
        print(f"Page '{self.title}' unfocused")