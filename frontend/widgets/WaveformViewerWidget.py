from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput


class WaveformViewerWidget(QWidget):
    def __init__(self, navHeight=100):
        super().__init__()
        self.plotTypeMenu = DropDownMenu(options=["Waveform", "FFT"], 
                                         onChoose=self.changeView, firstSelected=True)
        self.xAxisScale = DropDownMenu(options=["Linear X", "Log X"], 
                                       onChoose=self.changeView, firstSelected=True)
        self.yAxisScale = DropDownMenu(options=["Linear Y", "Log Y"], 
                                       onChoose=self.changeView, firstSelected=True)
        self.paddingInput = TextInput("Padding", default="0", regex="^[0-9]*$", on_change=self.changeView, layout='h')

        self.plotLayout = pg.GraphicsLayoutWidget(show=True)
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)
        self.waveformPlot2.setMaximumHeight(navHeight)

        self.x = []
        self.y = []

        layout = QVBoxLayout()
        self.initUI(layout)

    def initUI(self, layout):
        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))

        self.waveformPlot1.getViewBox().setMouseEnabled(y=False)
        self.waveformPlot1.showGrid(x=True, y=True)
        self.waveformPlot2.getViewBox().setMouseEnabled(y=False, x=False)

        # Set a LinearRegionItem to select a region of the waveform
        self.region.setZValue(10)
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)

        self.waveformPlot1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self.update)
        self.waveformPlot1.sigRangeChanged.connect(self.updateRegion)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.plotTypeMenu)
        hlayout.addWidget(self.xAxisScale)
        hlayout.addWidget(self.yAxisScale)
        hlayout.addWidget(self.paddingInput)
        hlayout.addStretch(1)
        hlayout.addWidget(Button("Autoscale", on_click=lambda: self.changeView(None)))
        layout.addLayout(hlayout)
        layout.addWidget(self.plotLayout)
        self.setLayout(layout)


    def changeView(self, view):
        self.redraw()
        self.waveformPlot1.autoRange()
        self.waveformPlot1.setAutoVisible(y=True)
        self.waveformPlot1.enableAutoRange(axis='y')
        self.waveformPlot1.setMouseEnabled(x=True, y=False)

    def redraw(self, _=None):
        self.plot(self.x, self.y)

    def plot(self, x, y):
        self.x = x
        self.y = y

        if self.paddingInput.text() == "":
            padding = 0
        else:
            padding = int(self.paddingInput.text())
        if padding > len(x) // 2:
            padding = len(x) // 2
        # Add zero padding
        y = np.pad(y, (padding, padding), 'constant')
        xLast = x[-1] + (x[1] - x[0]) * padding * 2
        x = np.linspace(x[0], xLast, len(y))

        # Clear the plots
        self.waveformPlot1.clear()
        self.waveformPlot2.clear()
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)

        plotType = self.plotTypeMenu.selected
        if plotType == "FFT":
            # compute the FFT
            y = np.abs(np.fft.rfft(y)) / len(y)
            x = np.fft.rfftfreq(len(x), d=(x[1]-x[0]))
        elif plotType == "Waveform":
            pass
        else:
            raise ValueError("Invalid plot type")
        
        xlog = True if self.xAxisScale.selected == "Log X" else False
        ylog = True if self.yAxisScale.selected == "Log Y" else False
        self.waveformPlot1.setLogMode(x=xlog, y=ylog)
        self.waveformPlot2.setLogMode(x=xlog, y=ylog)

        # Plot the waveform
        self.waveformPlot1.plot(x, y)
        self.waveformPlot2.plot(x, y)

        self.waveformPlot2.autoRange()
        self.updateRegion(self.waveformPlot1.getViewBox(), self.waveformPlot1.getViewBox().viewRange())


    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.waveformPlot1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)