from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget
from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

from backend.ParamObject import *



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
