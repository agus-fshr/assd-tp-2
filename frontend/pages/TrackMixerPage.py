from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QDialog, QProgressBar, QDesktopWidget, QCheckBox, QFileDialog, QRadioButton
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.widgets.CardWidgets import CardWidget, CardListWidget
from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget
from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget
       
import numpy as np

from dataclasses import dataclass

class CustomDialog(QDialog):
        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                event.accept()
            else:
                super().keyPressEvent(event)


@dataclass
class TrackMixData:
    name: str
    volume: float
    framerate: int
    muted: bool = False



class TrackCardWidget(CardWidget):
    changed = pyqtSignal(float, bool)

    def __init__(self, name, framerate, instrumentName, effectName, width=None, height=None):
        
        self.track = TrackMixData(name=name, volume=1.0, framerate=framerate)
        
        self.slider = Slider("Volumen", interval=(0.01, 1.5), step=0.01, defaultVal=1.0)
        self.slider.slider.sliderReleased.connect(self.on_control_change)
        # self.checkbox = QCheckBox("Activar control de ganancia")
        # self.checkbox.stateChanged.connect(self.on_control_change)
        self.radio = QRadioButton("Mute")
        self.radio.clicked.connect(self.on_control_change)
        VcardLayout = QVBoxLayout()
        VcardLayout.addWidget(self.slider)
        # VcardLayout.addWidget(self.checkbox)
        VcardLayout.addWidget(self.radio)

        subtitle = f"{instrumentName}\n{effectName}"
        
        super().__init__(child=VcardLayout, title=name, subtitle=subtitle, width=width, height=height)

    def on_control_change(self, _=None, __=None):
        self.track.volume = self.slider.value()
        # self.track.gainControl = self.checkbox.isChecked()
        self.track.muted = self.radio.isChecked()
        self.changed.emit(self.track.volume, self.track.muted)



class TrackMixerPage(BaseClassPage):

    title = "Track Mixer"    

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.hint = QLabel("Select Tracks:")
        self.trackSelector = DropDownMenu("Add tracks", onChoose=self.on_track_selected, showSelected=False)
        self.trackPopper = Button("Pop last track", on_click=self.pop_last_track, background_color="lightcoral", hover_color="white")

        self.batchSize = NumberInput("Plot resolution", interval=(1, 4410), step=1, default=1000, on_change=self.display_mix)

        self.trackViewer = WaveformViewerWidget(plotTypeMenu=False, scaleMenu=False, addonsMenu=False, settingsBtn=False)
        # self.trackList = CardListWidget()

        self.addEffectSelector = DropDownMenu("Add Effect", onChoose=self.on_effect_selected, showSelected=False)
        
        self.playSelected = Button("Set Visible Audio to Play", on_click=self.play_selected)
        saveWAVButton = Button("Export WAV", on_click=self.saveWAV, background_color="lightblue", hover_color="white")

        self.masterVolume = Slider("Master Volume", interval=(0.01, 1.5), step=0.01, defaultVal=1.0)
        self.masterVolume.slider.sliderReleased.connect(self.display_mix)
        self.masterVolume.setMaximumWidth(400)
        self.activateGainControl = QCheckBox("Dynamic Range Compression")
        self.activateGainControl.stateChanged.connect(self.display_mix)


        self.trackCardList = CardListWidget()
        self.trackCardList.setMaximumWidth(450)

        # Setup audio player widget
        self.player = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Local widgets (used only in the initUI method)
        trackHlayout = QHBoxLayout()
        controlsHlayout = QHBoxLayout()
        contentHlayout = QHBoxLayout()

        # Setup top layout
        trackHlayout.addWidget(self.hint)
        trackHlayout.addWidget(self.trackSelector)
        trackHlayout.addSpacing(20)
        trackHlayout.addWidget(self.trackPopper)
        trackHlayout.addStretch(1)
        trackHlayout.addWidget(self.batchSize)

        # controlsHlayout.addWidget(self.gainAdjust)
        # controlsHlayout.addWidget(self.activateGainControl)
        # controlsHlayout.addSpacing(20)
        controlsHlayout.addWidget(self.playSelected)
        controlsHlayout.addStretch(1)
        controlsHlayout.addWidget(saveWAVButton)
        controlsHlayout.addStretch(1)
        controlsHlayout.addWidget(self.addEffectSelector)

        
        trackVLeftLayout = QVBoxLayout()
        trackVLeftLayout.addWidget(self.masterVolume)
        trackVLeftLayout.addWidget(self.activateGainControl)
        trackVLeftLayout.addWidget(self.trackCardList)
        contentHlayout.addWidget(self.trackViewer)
        contentHlayout.addLayout(trackVLeftLayout)

        # Add widgets to page layout
        # layout.addWidget(self.track_selected)
        layout.addLayout(trackHlayout)
        layout.addLayout(controlsHlayout)
        layout.addWidget(self.player)
        layout.addLayout(contentHlayout)

        self.mix_array = np.zeros(1000)
        self.max_size = 1000
        self.framerate = 44100


    def saveWAV(self):
        self.model.audioPlayer.stop()
        self.model.audioPlayer.set_array(self.mix_array, self.framerate)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name = self.trackSelector.selected
        default_filename = name + "_out.wav"
        filename, _ = QFileDialog.getSaveFileName(self, "Save as WAV", default_filename, "WAV Files (*.wav)", options=options)
        if filename:
            self.model.audioPlayer.save_to_file(filename)


    def pop_last_track(self):
        self.trackCardList.popCard()
        self.display_mix()


    def try_effect_with_visible_data(self):
        effect = self.addEffectSelector.selected
        xmin, xmax = self.trackViewer.getViewRangeX()

        n0 = int(xmin * self.framerate)
        n1 = int(xmax * self.framerate)
        if n0 < 0:
            n0 = 0
        if n1 > len(self.mix_array):
            n1 = len(self.mix_array)

        cut_array = self.mix_array[n0:n1]
        cut_array = effect(cut_array)

        self.model.audioPlayer.set_array(cut_array, self.framerate)
        self.player.play()


    def on_effect_selected(self, name, effect):
        dynamicSettingsWidget = DynamicSettingsWidget(paramList=effect.params, title=f"{name} Settings")

        statusLabel = QLabel("")
        statusLabel.setText("Applying effect...")
        statusLabel.hide()
        # create a dialog to show the settings and add a button to apply or cancel
        dialog = CustomDialog()
        dialog.setWindowTitle(f"{name} Settings")
        dialog.setLayout(QVBoxLayout())
        dialog.setModal(False)
        dialog.layout().addWidget(dynamicSettingsWidget)
        dialog.layout().addWidget(Button("Try Effect with Visible Audio", on_click=self.try_effect_with_visible_data, background_color="lightblue"))
        dialog.layout().addWidget(Button("Compute and Add Effect", on_click=dialog.accept, background_color='lightgreen'))
        dialog.layout().addWidget(statusLabel)
        dialog.layout().addWidget(Button("Cancel", on_click=dialog.reject, background_color="lightcoral"))

        if dialog.exec_():
            statusLabel.show()
            self.mix_array = effect(self.mix_array)
            self.display_mix()
            print("Effect applied")


    # Refresh dropdown options looking for newly imported MIDI files
    def refresh_track_options(self):
        options = list(self.model.synthesized_tracks.keys())
        self.trackSelector.set_options(options)


    def play_selected(self):
        print("Play selected")
        xmin, xmax = self.trackViewer.getViewRangeX()

        n0 = int(xmin * self.framerate)
        n1 = int(xmax * self.framerate)
        if n0 < 0:
            n0 = 0
        if n1 > len(self.mix_array):
            n1 = len(self.mix_array)

        self.model.audioPlayer.set_array(self.mix_array[n0:n1], self.framerate)
        self.player.play()


    # SET THE ORIGINAL CLEAN TRACK
    def on_track_selected(self, _):
        name = self.trackSelector.selected
        track_data = self.model.synthesized_tracks[name]
        array = track_data["track_array"]
        framerate = track_data["framerate"]
        instrumentName = track_data["instrument"]
        effectName = track_data["effect"]

        self.max_size = np.max([self.max_size, len(array)])

        card = TrackCardWidget(name, framerate, instrumentName, effectName)
        card.changed.connect(self.display_mix)
        self.trackCardList.addCard(card)

        self.display_mix()


    # Callback for when a MIDI file is selected from the dropdown
    def display_mix(self, _=None):

        self.mix_array = np.zeros(1000)

        for trackCard in self.trackCardList:
            track = trackCard.track
            array = self.model.synthesized_tracks[track.name]["track_array"]

            if len(self.mix_array) < len(array):
                size_needed = len(array) - len(self.mix_array)
                self.mix_array = np.append(self.mix_array, np.zeros(size_needed + 1))

            if not track.muted:
                self.mix_array[:len(array)] += array * track.volume
                
        if self.activateGainControl.isChecked():
            self.mix_array, _ = self.dynamic_range_compression(self.mix_array, segment_size=500, threshold=0.98)

        self.mix_array = self.mix_array * self.masterVolume.value()
        
        array_batches = np.array_split(self.mix_array, self.mix_array.size // self.batchSize.value())
        # iterate over
        max_env = []
        min_env = []
        for batch in array_batches:
            max_env.append(np.max(batch))
            min_env.append(np.min(batch))

        time = np.arange(len(array_batches)) * (self.batchSize.value() / self.framerate)

        self.trackViewer.plotEnvelope(time, max_env, min_env)

        self.trackViewer.plotInfiniteLine(y=1.0)
        self.trackViewer.plotInfiniteLine(y=-1.0)



    @staticmethod
    def dynamic_range_compression(input_wave, segment_size=500, threshold=1.0):
        # Calculate the number of segments
        num_segments = len(input_wave) // segment_size

        # Initialize output wave
        output_wave = np.zeros_like(input_wave)

        # Initialize the volume adjustment factors
        volume_adjustment_factors = np.ones(num_segments + 2)

        # First step: calculate the volume adjustment factors
        for i in range(num_segments):
            # Extract the current segment and the next segment
            current_segment = input_wave[i*segment_size:(i+1)*segment_size]
            next_segment = input_wave[(i+1)*segment_size:(i+2)*segment_size] if i+1 < num_segments else np.array([])

            # Calculate the maximum absolute amplitude of the current segment and the next segment
            max_amplitude_current = np.max(np.abs(current_segment))
            max_amplitude_next = np.max(np.abs(next_segment)) if next_segment.size else 0

            # If the maximum amplitude exceeds the threshold
            if max_amplitude_current > threshold or max_amplitude_next > threshold:
                # Calculate the volume adjustment factor
                volume_adjustment_factors[i+1] = threshold / max(max_amplitude_current, max_amplitude_next)

        # Second step: apply the volume adjustment factors
        for i in range(num_segments):
            # Extract the current segment
            segment = input_wave[i*segment_size:(i+1)*segment_size]

            # Calculate the volume adjustment ramp
            volume_adjustment_ramp = np.linspace(volume_adjustment_factors[i], volume_adjustment_factors[i+1], segment_size)

            # Apply the volume adjustment ramp to the segment
            output_wave[i*segment_size:(i+1)*segment_size] = segment * volume_adjustment_ramp

        # Process the remaining samples in the input wave, if any
        if len(input_wave) % segment_size != 0:
            segment = input_wave[num_segments*segment_size:]
            volume_adjustment_ramp = np.linspace(volume_adjustment_factors[-2], volume_adjustment_factors[-1], len(segment))
            output_wave[num_segments*segment_size:] = segment * volume_adjustment_ramp

        return output_wave, volume_adjustment_factors
    


    def load_effect_options(self):
        options = {}
        for effect in self.model.effects:
            options[effect.name] = effect
        self.addEffectSelector.set_options(options)



    # Refresh dropdown options looking for new MIDI files
    def on_tab_focus(self):
        self.refresh_track_options()
        self.load_effect_options()