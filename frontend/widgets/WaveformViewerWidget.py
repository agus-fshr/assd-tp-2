from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QGridLayout
from PyQt5.QtGui import QTransform

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput

class WaveformViewerWidget(QWidget):
    def __init__(self, navHeight=100, onFFT = lambda f, x: None):
        super().__init__()
        pg.setConfigOptions(imageAxisOrder='row-major')

        self.plotTypeMenu = DropDownMenu(options=["Waveform", "FFT", "Spectrogram"], 
                                         onChoose=self.changeView, firstSelected=True)
        self.xAxisScale = DropDownMenu(options=["Linear X", "Log X"], 
                                       onChoose=self.changeView, firstSelected=True)
        self.yAxisScale = DropDownMenu(options=["Linear Y", "Log Y"], 
                                       onChoose=self.changeView, firstSelected=True)
        self.paddingInput = TextInput("Padding", default="0", regex="^[0-9]*$", on_change=self.changeView, layout='h')

        self.onFFT = onFFT

        self.plotLayout = pg.GraphicsLayoutWidget(show=True)
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)
        
        self.histogramPlot = pg.HistogramLUTWidget(gradientPosition="left")
        self.histogramPlot.setMinimumWidth(150)
        self.histogramPlot.hide()

        # self.histogramPlot.setMaximumWidth(navHeight)
        self.waveformPlot2.setMaximumHeight(navHeight)

        self.x = []
        self.y = []
        self.plotItems = []

        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))

        self.waveformPlot1.getViewBox().setMouseEnabled(y=False, x=True)
        self.waveformPlot1.showGrid(x=True, y=True)
        self.waveformPlot2.getViewBox().setMouseEnabled(y=False, x=False)

        # Set a LinearRegionItem to select a region of the waveform
        self.region.setZValue(10)
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)

        self.region.sigRegionChanged.connect(self.update)
        self.waveformPlot1.sigRangeChanged.connect(self.updateRegion)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.plotTypeMenu)
        hlayout.addWidget(self.xAxisScale)
        hlayout.addWidget(self.yAxisScale)
        hlayout.addWidget(self.paddingInput)
        hlayout.addStretch(1)
        hlayout.addWidget(Button("Autoscale", on_click=lambda: self.changeView(None)))
        plotsHLayout = QHBoxLayout()
        plotsHLayout.addWidget(self.plotLayout)
        plotsHLayout.addWidget(self.histogramPlot)

        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addLayout(plotsHLayout)
        self.setLayout(layout)        


    def changeView(self, view):
        self.redraw()
        if self.plotTypeMenu.selected != "Spectrogram":
            self.waveformPlot1.autoRange()
            self.waveformPlot1.enableAutoRange(axis='y')
            self.waveformPlot1.setAutoVisible(y=True)
            self.waveformPlot1.setMouseEnabled(x=True, y=False)
        else:
            self.waveformPlot1.disableAutoRange()
            self.waveformPlot1.setAutoVisible(y=False)
            self.waveformPlot1.setMouseEnabled(x=True, y=True)

    def redraw(self, _=None):
        self.plot(self.x, self.y)

    def scatter(self, x, y):
        self.waveformPlot1.plot(x, y, pen=None, symbol='x', symbolSize=20, symbolBrush=(255, 0, 0))
        self.waveformPlot2.plot(x, y, pen=None, symbol='x', symbolSize=20, symbolBrush=(255, 0, 0))

    def plot(self, x, y):
        self.x = x
        self.y = y

        Ts = x[1] - x[0]    # sampling interval

        x, y = self.setPadding(x, y, Ts)

        # Clear the plots
        for item in self.plotItems:
            self.waveformPlot1.removeItem(item)
        self.waveformPlot1.clear()
        self.waveformPlot2.clear()
        self.plotItems = []

        self.waveformPlot2.addItem(self.region, ignoreBounds=True)

        plotType = self.plotTypeMenu.selected
        if plotType == "FFT":
            # compute the FFT
            y = np.abs(np.fft.rfft(y)) / len(y)
            x = np.fft.rfftfreq(len(x), d=Ts)
            if self.onFFT is not None:
                self.onFFT(x, y)
            self.waveformPlot1.setLabel('bottom', "Frequency", units='Hz')
            self.waveformPlot2.setLabel('bottom', "Frequency", units='Hz')
        elif plotType == "Waveform":
            self.waveformPlot1.setLabel('bottom', "Time", units='s')
            self.waveformPlot2.setLabel('bottom', "Time", units='s')
            pass
        elif plotType == "Spectrogram":
            self.waveformPlot1.setLabel('bottom', "Time", units='s')
            self.waveformPlot2.setLabel('bottom', "Time", units='s')
            pass
        else:
            raise ValueError("Invalid plot type")
        
        xlog = True if self.xAxisScale.selected == "Log X" else False
        ylog = True if self.yAxisScale.selected == "Log Y" else False
        
        if plotType != "Spectrogram":
            # Set the scale
            self.waveformPlot1.setLogMode(x=xlog, y=ylog)
            self.waveformPlot2.setLogMode(x=xlog, y=ylog)

            # Plot the waveform
            self.waveformPlot1.plot(x, y)
            self.waveformPlot2.plot(x, y)
            self.histogramPlot.hide()
            self.waveformPlot1.enableAutoRange(axis='y')
        else:
            # Plot the spectrogram
            f, t, Sxx = signal.spectrogram(y, fs=1/Ts)

            if ylog:
                Sxx = np.log10(Sxx)

            x_scale = (x.max() - x.min()) / Sxx.shape[1]
            y_scale = (f.max() - f.min()) / Sxx.shape[0]

            tr = QTransform()
            tr.scale(x_scale, y_scale)

            img = pg.ImageItem()
            img.setImage(Sxx)
            img.setPos(0, 0)
            img.setTransform(tr)            

            self.histogramPlot.setImageItem(img)
            self.histogramPlot.setLevels(np.min(Sxx), np.max(Sxx))
            # hist.setLevels(0, 1)
            self.histogramPlot.gradient.restoreState(
                {'mode': 'rgb', 
                'ticks': [(0.5, (0, 182, 188, 255)),
                        (1.0, (246, 111, 0, 255)),
                        (0.0, (75, 0, 113, 255))]})
            # hist.gradient.loadPreset('flame')
            self.histogramPlot.show()

            self.waveformPlot1.addItem(img)

            self.plotItems.append(img)
            
            self.waveformPlot1.setLogMode(x=False, y=False)
            self.waveformPlot1.setLabel('left', "Frequency", units='Hz')
            self.waveformPlot1.autoRange()
            
            self.waveformPlot2.setLogMode(x=False, y=False)
            self.waveformPlot2.plot(x, y)

        self.waveformPlot2.autoRange()
        self.updateRegion(self.waveformPlot1.getViewBox(), self.waveformPlot1.getViewBox().viewRange())

        if plotType != "Spectrogram":
            self.waveformPlot1.setAutoVisible(y=True)
        else:
            self.waveformPlot1.setAutoVisible(y=False)


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


    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.waveformPlot1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)






































# win = pg.QtGui.QMainWindow()
# widget = QWidget()
# win.setCentralWidget(widget)

# layout = QGridLayout()
# widget.setLayout(layout)
# layout.setSpacing(0)

# view = pg.GraphicsView()
# vb = pg.ViewBox()
# vb.setAspectLocked()
# view.setCentralItem(vb)
# layout.addWidget(view, 0, 1, 3, 1)  # TUKO

# hist = pg.HistogramLUTWidget(gradientPosition="left")
# layout.addWidget(hist, 0, 2)


# monoRadio = QtWidgets.QRadioButton('mono')
# rgbaRadio = QtWidgets.QRadioButton('rgba')
# layout.addWidget(monoRadio, 1, 2)
# layout.addWidget(rgbaRadio, 2, 2)
# monoRadio.setChecked(True)


# def setLevelMode():
#     mode = 'mono' if monoRadio.isChecked() else 'rgba'
#     hist.setLevelMode(mode)


# monoRadio.toggled.connect(setLevelMode)

# data = pg.gaussianFilter(np.random.normal(size=(256, 256, 3)), (20, 20, 0))
# for i in range(32):
#     for j in range(32):
#         data[i*8, j*8] += .1
# img = pg.ImageItem(data)
# vb.addItem(img)
# vb.autoRange()

# hist.setImageItem(img)

# if __name__ == '__main__':
#     pg.exec()
