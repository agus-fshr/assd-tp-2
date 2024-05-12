from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QDialog, QLabel, QSpinBox
from PyQt5.QtGui import QTransform
from PyQt5.QtCore import pyqtSignal, Qt

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput
from .DynamicSettingsWidget import DynamicSettingsWidget
from backend.utils.ParamObject import ParameterList, NumParam, TextParam, BoolParam, ChoiceParam


class WaveformViewerWidget(QWidget):
    def __init__(self, navHeight=100, onFFT = lambda f, x: None, onEvent = None):
        super().__init__()

        self.plot = pg.PlotItem()
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)

        
        self.histogramPlot = pg.HistogramLUTWidget(gradientPosition="left")
        self.histogramPlot.setMinimumWidth(180)
        self.histogramPlot.hide()
        self.histogramPlot.sigLevelChangeFinished.connect(self.histogramLevelsChanged)

        # self.histogramPlot.setMaximumWidth(navHeight)
        self.waveformPlot2.setMaximumHeight(navHeight)

        self.data = None  # x, y
        self.histDefaultLevels = None
        self.histLastLevels = None

        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))

        self.waveformPlot1.getViewBox().setMouseEnabled(y=False, x=True)
        self.waveformPlot1.showGrid(x=True, y=True)
        self.waveformPlot2.getViewBox().setMouseEnabled(y=False, x=False)

        # Set a LinearRegionItem to select a region of the waveform
        self.region.setZValue(10)
        self.region.sigRegionChanged.connect(self.updatePlot1)
        self.waveformPlot1.sigRangeChanged.connect(self.updateRegion)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.plotTypeMenu)
        hlayout.addWidget(self.xAxisScale)
        hlayout.addWidget(self.yAxisScale)
        hlayout.addWidget(self.paddingInput)
        hlayout.addSpacing(20)
        hlayout.addWidget(Button("Settings", on_click = self.settingsDialog.exec ))
        hlayout.addStretch(1)
        hlayout.addWidget(Button("Autoscale", on_click=self.autoRange))
        plotsHLayout = QHBoxLayout()
        plotsHLayout.addWidget(self.plotLayout)
        plotsHLayout.addWidget(self.histogramPlot)

        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addLayout(plotsHLayout)
        self.setLayout(layout)        
    

    def reloadPlot(self, _=None):
        ''' Plot with the same data '''
        print("reloadPlot")
        x, y = self.data
        self.plot(x, y)


    def redraw(self, _=None):
        ''' Plot with the same data without changing the view or the scale '''
        print("redraw")
        self.clear()
        x, y = self.data
        Ts = x[1] - x[0]    # sampling interval
        x, y = self.setPadding(x, y, Ts)
        x, y = self.computePlotData(x, y, Ts)
        self.plotComputedData(x, y)
        if self.plotTypeMenu.selected == "Spectrogram" and self.histLastLevels is not None:
            self.histogramPlot.setLevels(*self.histLastLevels)
        self.updateScale()


    def scatter(self, x, y):
        self.waveformPlot1.plot(x, y, pen=None, symbol='x', symbolSize=20, symbolBrush=(255, 0, 0))
        self.waveformPlot2.plot(x, y, pen=None, symbol='x', symbolSize=20, symbolBrush=(255, 0, 0))


    def plot(self, x, y):
        print("plot")
        if len(x) == 0 or len(y) == 0:
            print("No data to plot")
            return
        # save the data
        self.data = x, y

        Ts = x[1] - x[0]    # sampling interval
        self.clear()

        x, y = self.setPadding(x, y, Ts)
        x, y = self.computePlotData(x, y, Ts)
        self.updateLabels()
        self.plotComputedData(x, y)
        self.updateScale()
        self.autoRange()


    def autoRange(self):
        print("autoRange")
        self.waveformPlot1.autoRange()
        self.waveformPlot2.autoRange()
        self.histogramPlot.autoHistogramRange()
        if self.histDefaultLevels is not None:
            self.histogramPlot.setLevels(*self.histDefaultLevels)
            print(f"autoRange histDefaultLevels: {self.histDefaultLevels}")
        self.updateRegion(self.waveformPlot1.getViewBox(), self.waveformPlot1.getViewBox().viewRange())


    def plotComputedData(self, x, y):
        print("plotComputedData")
        if self.plotTypeMenu.selected in ["Waveform", "FFT"]:
            self.waveformPlot1.plot(x, y)
            self.waveformPlot2.plot(x, y)
        elif self.plotTypeMenu.selected == "Spectrogram":
            self.waveformPlot2.plot(x, y)


    def updateScale(self):
        print("updateScale")
        xlog = True if self.xAxisScale.selected == "Log X" else False
        ylog = True if self.yAxisScale.selected == "Log Y" else False
        plotType = self.plotTypeMenu.selected
        self.waveformPlot1.enableAutoRange(x=xlog, y=ylog)
        if plotType in ["FFT", "Waveform"]:
            self.waveformPlot1.setLogMode(x=xlog, y=ylog)
            self.waveformPlot2.setLogMode(x=xlog, y=ylog)
            self.waveformPlot1.setMouseEnabled(x=True, y=False)     # Disable y axis zoom
            self.waveformPlot1.setAutoVisible(y=True)               # Enable auto range to visible data for the y axis
            self.waveformPlot1.enableAutoRange(axis='y')
            self.histogramPlot.hide()                               # Hide the histogram
        elif plotType == "Spectrogram":
            self.waveformPlot1.setLogMode(x=False, y=False)
            self.waveformPlot2.setLogMode(x=False, y=False)
            self.waveformPlot1.setMouseEnabled(x=True, y=True)
            self.waveformPlot1.setAutoVisible(y=False)              # Disable auto range to visible data for the y axis
            self.waveformPlot1.disableAutoRange(axis='y')
            self.histogramPlot.show()                               # Show the histogram (for the spectrogram)



    def computePlotData(self, x, y, Ts):
        print("computePlotData")
        plotType = self.plotTypeMenu.selected
        if plotType == "FFT":
            # apply the window function
            window = self.settingsDialog["FFTWindow"]
            y = y * signal.get_window(window, len(y))
            y = np.abs(np.fft.rfft(y)) / len(y)
            x = np.fft.rfftfreq(len(x), d=Ts)
        elif plotType == "Waveform":
            pass
        elif plotType == "Spectrogram":
            nperseg = int(self.settingsDialog["nperseg"])
            noverlap = int(self.settingsDialog["noverlap"])
            window = self.settingsDialog["specWindow"]
            f, t, Sxx = signal.spectrogram(y, fs=1/Ts, nperseg=nperseg, noverlap=noverlap, scaling='spectrum', mode='magnitude')

            if self.yAxisScale.selected == "Log Y":
                Sxx = np.log10(Sxx)

            x_scale = (x.max() - x.min()) / Sxx.shape[1]
            y_scale = (f.max() - f.min()) / Sxx.shape[0]
            tr = QTransform()
            tr.scale(x_scale, y_scale)

            img = pg.ImageItem()
            img.setImage(Sxx)
            img.setPos(0, 0)
            img.setTransform(tr)            

            self.histogramPlot.sigLevelChangeFinished.disconnect(self.histogramLevelsChanged)   # DO
            self.histogramPlot.setImageItem(img)
            self.histDefaultLevels = (np.min(Sxx), np.max(Sxx))
            self.histogramPlot.setLevels(*self.histDefaultLevels)
            self.histogramPlot.gradient.restoreState(
                {'mode': 'rgb', 
                'ticks': [(0.5, (0, 182, 188, 255)),
                        (1.0, (246, 111, 0, 255)),
                        (0.0, (75, 0, 113, 255))]})
            # hist.gradient.loadPreset('flame')
            self.histogramPlot.sigLevelChangeFinished.connect(self.histogramLevelsChanged)
            self.waveformPlot1.addItem(img)
        else:
            raise ValueError("Invalid plot type")
        
        return x, y

    def clear(self):
        # Clear the plots
        self.waveformPlot1.clear()
        self.waveformPlot2.clear()
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)
        self.histogramPlot.hide()


    def updateLabels(self):
        print("updateLabels")
        plotType = self.plotTypeMenu.selected
        if plotType == "FFT":
            self.waveformPlot1.setLabel('bottom', "Frequency", units='Hz')
            self.waveformPlot2.setLabel('bottom', "Frequency", units='Hz')
        elif plotType == "Waveform":
            self.waveformPlot1.setLabel('bottom', "Time", units='s')
            self.waveformPlot2.setLabel('bottom', "Time", units='s')
        elif plotType == "Spectrogram":
            self.waveformPlot1.setLabel('bottom', "Time", units='s')
            self.waveformPlot2.setLabel('bottom', "Time", units='s')
        else:
            raise ValueError("Invalid plot type")


    def setPadding(self, x, y, Ts):
        if self.paddingInput.text() == "":
            padding = 0
        else:
            padding = int(self.paddingInput.text())
        if padding > len(x) // 2:
            padding = len(x) // 2
        # Add zero padding
        y = np.pad(y, (padding, padding), 'constant')
        xLast = x[-1] + Ts * padding * 2
        x = np.linspace(x[0], xLast, len(y))
        return x, y


    def updatePlot1(self):
        ''' Update the waveform plot 1 when the region is changed '''
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.waveformPlot1.setXRange(minX, maxX, padding=0)


    def updateRegion(self, window, viewRange):
        ''' Update the region when the view range is changed'''
        rgn = viewRange[0]
        self.region.setRegion(rgn)


    def histogramLevelsChanged(self):
        ''' Save the last levels of the histogram '''
        self.histLastLevels = self.histogramPlot.getLevels()
        print(f"histogramLevelsChanged: {self.histLastLevels}")