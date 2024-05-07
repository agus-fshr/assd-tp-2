from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget
from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

from backend.ParamObject import *

import sympy as sp
import numpy as np

class TestPage(BaseClassPage):

    title = "TestPage"    

    def initUI(self, layout):
        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        leftVLayout = QVBoxLayout()

        self.params = ParameterList(
            NumParam('s', interval=(0, 10), value=1.0, step=0.01, text="Stretch"),
            NumParam('sr', interval=(44100, 192000), value=44100, step=100, text="Sample Rate"),
            # TextParam("eq", value="a*cos(wa*x)+b*cos(wb*x)+c*cos(wc*x)", text="Equation"),
            # NumParam("a", interval=(0, 5), value=2, step=0.01, text="a = Amplitude"),
            # NumParam("b", interval=(0, 5), value=0.8, step=0.01, text="b = Amplitude"),
            # NumParam("c", interval=(0, 5), value=0.2, step=0.01, text="c = Amplitude"),
            # NumParam("wa", interval=(0, 500), value=9, step=0.01, text="wa = Frequency [rad/s]"),
            # NumParam("wb", interval=(0, 500), value=2, step=0.01, text="wb = Frequency [rad/s]"),
            # NumParam("wc", interval=(0, 500), value=440, step=0.01, text="wc = Frequency [rad/s]"),
        )

        # Widgets
        dynSettings = DynamicSettingsWidget(paramList=self.params, title="Dynamic Settings")
        button = Button("Test", on_click=self.test)
        self.plotWidget = WaveformViewerWidget()

        leftVLayout.addWidget(button)
        leftVLayout.addSpacing(20)
        leftVLayout.addWidget(self.plotWidget)

        # Setup top layout
        topHLayout.addWidget(dynSettings)
        topHLayout.addSpacing(20)
        topHLayout.addLayout(leftVLayout)
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)


    def test(self):
        print("Test")

        # func = self.params.getFunction(eq="eq", var="x")

        stretch = self.params["s"]
        sample_rate = int(self.params["sr"])

        freq = np.arange(60, 1060) * 2 * np.pi
        freq = freq.astype(int)

        y = sample_rate / freq - 1/(2*stretch)
        y = y.astype(int)
        self.plotWidget.plot(freq, y)
