from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget

class InstrumentPage(BaseClassPage):
    
    title = "Instrument Testbench"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.instrumentSelector = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=self.on_effect_selected)

        self.freqSelector = NumberInput("Frequency", default=740, interval=(20, 2000), step=1)
        self.ampSelector = NumberInput("Amplitude", default=0.25, interval=(0, 1), step=0.01)
        self.durationSelector = NumberInput("Duration", default=0.0, interval=(0, 3), step=0.1)

        self.dynamicSettings = DynamicSettingsWidget()

        self.player = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        controlsHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.instrumentSelector)
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
        controlsHLayout.addWidget(Button("Play Note", on_click=self.play_note))
        controlsHLayout.addStretch(1)
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addLayout(controlsHLayout)
        layout.addWidget(self.player)
        layout.addSpacing(20)
        layout.addWidget(self.dynamicSettings)


    # Play the selected note
    def play_note(self):
        freq = self.freqSelector.value()
        amp = self.ampSelector.value()
        duration = self.durationSelector.value()

        instrument = self.instrumentSelector.selected
        effect = self.effectSelector.selected

        wave_array = instrument(freq, amp, duration)
        wave_array = effect(wave_array)
        self.model.audioPlayer.set_array(wave_array)
        self.model.audioPlayer.play()


    def refresh_instrument_options(self):
        options = {}
        for synth in self.model.synthesizers:
            options[synth.name] = synth
        self.instrumentSelector.set_options(options, firstSelected=True)

    def refresh_effect_options(self):
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


    # Refresh dropdown options looking for new Instruments and Effects
    def on_tab_focus(self):
        self.refresh_instrument_options()
        self.refresh_effect_options()
