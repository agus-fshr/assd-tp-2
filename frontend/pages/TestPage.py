from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget
from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

from backend.ParamObject import *

import sympy as sp
import numpy as np


import numpy as np

class ModFunction():
    def __init__(self, type="linear", n=1.0):
        n = np.clip(n, 0.1, 10)
        match type:
            case "linear":
                self.func = lambda x: x
            case "exp":
                self.func = lambda x: (np.exp(n*x) - 1) / (np.exp(n) - 1)
            case "log":
                self.func = lambda x: np.log(n*x + 1) / np.log(n + 1)
            case "poly":
                self.func = lambda x: x**n
            case "polyFlatTop":
                self.func = lambda x: 1 - (1 - x)**n
            case "sin":
                self.func = lambda x: (np.sin(x * np.pi / 2)) ** n
            case "cos":
                self.func = lambda x: 1 - (np.cos(x * np.pi / 2)) ** n


    def __call__(self, x):
        if np.min(x) < 0.0 or np.max(x) > 1.0:
            raise ValueError("Input value must be between 0 and 1")
        return self.func(x)

    def mod(self, x, x0=0.0, x1=0.0, y0=0.0, y1=0.0):
        return y0 + (y1 - y0) * self((x - x0) / (x1 - x0))


class LinearADSR():
    def __init__(self, k, A, D, R, tone_duration):
        self.k = k
        self.attack = A
        self.decay = D
        self.release = R
        self.tone_duration = tone_duration

        points = int((self.tone_duration + R) * 44100)
        self.t = np.linspace(0, self.tone_duration + R, points, endpoint=False)

    def time(self):
        return self.t

    def __call__(self):
        """ Generate the ADSR envelope for a given time array t and note duration
        t: numpy array of time values
        duration: total duration of the note in seconds (from on to off)
        """
        # Calculate the sustain phase duration
        k = self.k
        A = self.attack
        D = self.decay
        R = self.release
        S = self.tone_duration - self.attack - self.decay        
        t = self.t

        # Create an output array of the same shape as t
        output = np.zeros_like(t)
        
        attFunc = ModFunction("polyFlatTop", 3)
        decFunc = ModFunction("polyFlatTop", 3)
        relFunc = ModFunction("polyFlatTop", 3)

        # Attack phase
        attack_mask = t < A
        output[attack_mask] = attFunc.mod(t[attack_mask], x1=A, y1=k)
        
        # Decay phase
        decay_mask = (t >= A) & (t < A + D)
        output[decay_mask] = decFunc.mod(t[decay_mask], x0=A, x1=A+D, y0=k*1, y1=1)
        
        # Sustain phase
        sustain_mask = (t >= A + D) & (t < A + D + S)
        output[sustain_mask] = 1.0
        
        # Release phase
        release_mask = (t >= A + D + S) & (t < A + D + S + R)
        output[release_mask] = relFunc.mod(t[release_mask], x0=A+D+S, x1=A+D+S+R, y0=1, y1=0)
                
        return output


class TestPage(BaseClassPage):

    title = "TestPage"    

    def initUI(self, layout):
        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()
        leftVLayout = QVBoxLayout()

        self.params = ParameterList(
            NumParam('k', interval=(0, 10), value=2.0, step=0.01, text="k"),
            NumParam('A', interval=(0, 10), value=0.1, step=0.01, text="Attack"),
            NumParam('D', interval=(0, 10), value=0.1, step=0.01, text="Decay"),
            NumParam('R', interval=(0, 10), value=0.3, step=0.01, text="Release"),
            NumParam('dur', interval=(0, 10), value=1.0, step=0.01, text="Total Duration"),

            # TextParam("eq", value="a*cos(wa*x)+b*cos(wb*x)+c*cos(wc*x)", text="Equation"),
            # NumParam("a", interval=(0, 5), value=2, step=0.01, text="a = Amplitude"),
            # NumParam("b", interval=(0, 5), value=0.8, step=0.01, text="b = Amplitude"),
            # NumParam("c", interval=(0, 5), value=0.2, step=0.01, text="c = Amplitude"),
            # NumParam("wa", interval=(0, 500), value=9, step=0.01, text="wa = Frequency [rad/s]"),
            # NumParam("wb", interval=(0, 500), value=2, step=0.01, text="wb = Frequency [rad/s]"),
            # NumParam("wc", interval=(0, 500), value=440, step=0.01, text="wc = Frequency [rad/s]"),
        )

        # Widgets
        dynSettings = DynamicSettingsWidget(paramList=self.params, title="Dynamic Settings", on_edit=self.on_edit)
        button = Button("Test", on_click=self.on_edit)
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


    def on_edit(self, k=None, v=None):

        # func = self.params.getFunction(eq="eq", var="x")
        k = self.params["k"]
        a = self.params["A"]
        d = self.params["D"]
        r = self.params["R"]
        duration = self.params["dur"]

        if duration < a + d:
            duration = a + d

        adsr = LinearADSR(k, a, d, r, duration)

        y = adsr()
        t = adsr.time()
        
        # y = y.astype(int)
        self.plotWidget.plot(t, y)
