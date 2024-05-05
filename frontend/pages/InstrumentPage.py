from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget

import pyqtgraph as pg
import numpy as np

class InstrumentPage(BaseClassPage):
    
    title = "Instrument Testbench"

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.instrumentSelector = DropDownMenu("Select Instrument", onChoose=self.on_instrument_selected)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=self.on_effect_selected)
        self.load_instrument_options()
        self.load_effect_options()

        self.freqSelector = NumberInput("Frequency", default=440, interval=(20, 10000), step=1)
        self.ampSelector = NumberInput("Amplitude", default=0.5, interval=(0, 1), step=0.01)
        self.durationSelector = NumberInput("Duration", default=0.4, interval=(0, 3), step=0.1)
        synthButton = Button("Synthesize", on_click=self.synthesize, background_color="lightgreen", hover_color="white")
        synthButton.setFixedWidth(150)

        self.dynamicSettings = DynamicSettingsWidget()
        self.on_instrument_selected(self.model.synthesizers[0].name, self.model.synthesizers[0])

        # Setup audio player widget
        self.player = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Set waveform plotter
        self.plotLayout = pg.GraphicsLayoutWidget(show=True)
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)
        self.waveformPlot2.setMaximumHeight(100)
        self.waveformPlot1.getViewBox().setMouseEnabled(y=False)
        self.waveformPlot1.showGrid(x=True, y=True)
        self.waveformPlot2.getViewBox().setMouseEnabled(y=False, x=False)

        # Set a LinearRegionItem to select a region of the waveform
        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))
        self.region.setZValue(10)
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)

        self.waveformPlot1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self.update)
        self.waveformPlot1.sigRangeChanged.connect(self.updateRegion)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        controlsHLayout = QHBoxLayout()
        settingsHLayout = QHBoxLayout()

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
        controlsHLayout.addWidget(synthButton)
        controlsHLayout.addStretch(1)
        
        # Setup settings layout
        settingsHLayout.addWidget(self.dynamicSettings)
        vplotlay = QVBoxLayout()
        vplotlay.addWidget(self.player)
        vplotlay.addWidget(self.plotLayout)
        settingsHLayout.addLayout(vplotlay)

        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addLayout(controlsHLayout)
        layout.addLayout(settingsHLayout)


    # Synthesize a sound using the selected instrument and effect
    def synthesize(self):
        freq = self.freqSelector.value()
        amp = self.ampSelector.value()
        duration = self.durationSelector.value()

        instrument = self.instrumentSelector.selected
        effect = self.effectSelector.selected

        wave_array = instrument(freq, amp, duration)
        wave_array = effect(wave_array)

        # set time axis
        framerate = self.model.audioPlayer.framerate
        time = np.arange(len(wave_array)) / framerate

        wave_array = np.clip(wave_array, -1.0, 1.0)

        self.waveformPlot1.clear()
        self.waveformPlot2.clear()
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)
        self.waveformPlot1.plot(time, wave_array)
        self.waveformPlot2.plot(time, wave_array)
        # self.waveformPlot1.setXRange(0, len(wave_array)/framerate, padding=0)
        self.waveformPlot2.autoRange()

        self.updateRegion(self.waveformPlot1.getViewBox(), self.waveformPlot1.getViewBox().viewRange())

        self.model.audioPlayer.set_array(wave_array)
        self.player.play()

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.waveformPlot1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)


    def load_instrument_options(self):
        options = {}
        for synth in self.model.synthesizers:
            options[synth.name] = synth
        self.instrumentSelector.set_options(options, firstSelected=True)

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