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
            TextParam("N", value="1", text="Numerator"),
            TextParam("D", value="1 - 2*R*cos(w0)*Z**(-1) + R**2*Z**(-2)", text="Denominator"),

            NumParam("w0", interval=(0, np.pi), step=0.01, value=0.5, text="w0 = Frequency [rad]"),
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

        const = {
            "R": 0.9,
        }

        Num = self.params.getFunction(eq="N", var="Z", const=const)
        Den = self.params.getFunction(eq="D", var="Z", const=const)

        x = np.linspace(0, 2, 1000)

        Z = np.exp(1j * np.pi * x)

        H_abs = np.abs(Num(Z) / Den(Z))

        self.plotWidget.plot(x, H_abs)
