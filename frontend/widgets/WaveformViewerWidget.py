from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QDialog, QLabel, QSpinBox, QTextEdit
from PyQt5.QtGui import QTransform
from PyQt5.QtCore import pyqtSignal, Qt

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput
from .DynamicSettingsWidget import DynamicSettingsWidget
from backend.utils.ParamObject import ParameterList, NumParam, TextParam, BoolParam, ChoiceParam

ALLOWED_WINDOWS = ['barthann','bartlett','blackman','blackmanharris','bohman','boxcar','rectangular','flattop','hamming','hann','tukey',]


class AddonBaseClass(QDialog):
    def __init__(self, title="Undefined", on_apply=None, title_postfix=" Addon"):
        super().__init__()
        self.title = title
        self.on_apply = on_apply
        self.setWindowTitle(title + title_postfix)
        self.dataGetter = lambda: print("Data getter not set")
        self.vlayout = QVBoxLayout()

        self.initUI(self.vlayout)

        hlayout = QHBoxLayout()
        hlayout.addWidget(Button("Cerrar", on_click=self.accept, background_color="lightcoral"))
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.vlayout)
        self.layout.addLayout(hlayout)
        self.setLayout(self.layout)

    def initUI(self, layout):
        raise NotImplementedError("initUI method must be implemented in Addon subclass")

    def setDataGetter(self, dataGetter):
        self.dataGetter = dataGetter

    def showEvent(self, event):
        self.resize(500, 700)  # w, h               # Set size of the QDialog
        self.move(100, 100)  # X, Y                 # Set position of the QDialog
        self.setModal(False)
        super().showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
            if self.on_apply is not None:
                self.on_apply()
        else:
            super().keyPressEvent(event)


class AddonsMenu(DropDownMenu):
    def __init__(self, onChoose, dataGetter, addons=[]):
        for addon in addons:
            if not isinstance(addon, AddonBaseClass):
                raise ValueError("Addon should be an instance of AddonBaseClass")
            addon.setDataGetter(dataGetter)
        super().__init__(title="Addons", showSelected=False, onChoose=onChoose, options=addons)



class FindPeaksAddon(AddonBaseClass):
    def __init__(self):
        super().__init__(title="Find Visible Peaks")

    def initUI(self, layout):
        self.settings = ParameterList(
            NumParam("markerSize", value=20, interval=(1, 100), step=1, text="Marker Size"),
            NumParam("minHeight", value=0.1, interval=(0, 1), step=0.00001, text="Minimum Peak Height"),
            NumParam("minDistance", value=50, interval=(0.01, 1000), step=0.01, text="Minimum Peak Distance"),
            NumParam("threshold", value=0, interval=(0, 1), step=0.00001, text="Threshold (vertical distance to its neighboring samples)"),
        )
        settingsWidget = DynamicSettingsWidget(paramList=self.settings, on_edit=self.find_peaks, sliderRelease=False)
        settingsWidget.setMinimumHeight(350)
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        # self.textEdit.setMinimumHeight(100)
        # self.textEdit.setMaximumHeight(200)

        layout.addWidget(settingsWidget)
        layout.addWidget(Button("Capture Visible Peaks", on_click=self.find_peaks, background_color="lightgreen"))
        layout.addWidget(self.textEdit)

    def exec(self):
        self.find_peaks()
        super().exec()

    def find_peaks(self):
        data, plot1, plot2 = self.dataGetter()
        if data is None or plot1 is None:
            print("No data")
            return
        
        self.textEdit.clear()
        if data["type"] in ["FFT", "Waveform"]:
            x, y = data["visibleData"]

            yRange = y.max() - y.min()
            # search for peaks
            n_x_distance = int(self.settings["minDistance"] / (x[1] - x[0]))
            height = self.settings["minHeight"] * yRange
            threshold = self.settings["threshold"]
            peaks, _ = signal.find_peaks(y, height=height, distance=n_x_distance, threshold=threshold)
            peaks_x = x[peaks]
            peaks_y = y[peaks]
            
            # Order peaks by amplitude (from highest to lowest amplitude)
            peaks_x = peaks_x[np.argsort(peaks_y)[::-1]]
            peaks_y = peaks_y[np.argsort(peaks_y)[::-1]]

            peak_log_str = f"{len(peaks_x)} Peaks:\nx,\ty\n"
            for px, py in zip(peaks_x, peaks_y):
                peak_log_str += f"{px:.3f},\t{py:.5f}\n"
            self.textEdit.setPlainText(peak_log_str)

            mks = int(self.settings["markerSize"])
            plot1.plot(peaks_x, peaks_y, pen=None, symbol='x', symbolSize=mks, symbolBrush=(255, 0, 0))
            plot2.plot(peaks_x, peaks_y, pen=None, symbol='x', symbolSize=(mks//2)+1, symbolBrush=(255, 0, 0))

            # plot infinite horizontal lines (plot is a pg.PlotItem)
            height_inf_line = pg.InfiniteLine(pos=height, angle=0, pen=pg.mkPen('r', width=2, style=Qt.DashLine))
            plot1.addItem(height_inf_line)



class SettingsDialog(AddonBaseClass):
    def __init__(self, on_apply=None):
        super().__init__(title="Settings", on_apply=on_apply, title_postfix="")

    def initUI(self, layout):
        self.settings = ParameterList(
            NumParam("padding", value=0, interval=(0,10000), step=1, text="Signal Padding"),
            ChoiceParam("FFTWindow", options=ALLOWED_WINDOWS, value='rectangular', text="FFT Window"),
            ChoiceParam("specWindow", options=ALLOWED_WINDOWS, value='rectangular', text="Spectrogram Window"),
            NumParam("nperseg", value=1024, interval=(128, 8192), step=1, text="Spectrogram Window Size"),
            NumParam("noverlap", value=512, interval=(0, 4096), step=1, text="Spectrogram Window Overlap"),
        )
        self.dynSettings = DynamicSettingsWidget(self.settings, on_edit=self.on_apply)
        layout.addWidget(self.dynSettings)

    def __getitem__(self, key):
        return self.settings.__getitem__(key)



class WaveformViewerWidget(QWidget):
    def __init__(self, navHeight=100, plotTypeMenu=True, scaleMenu=True, settingsBtn=True, addonsMenu=True):
        super().__init__()
        pg.setConfigOptions(imageAxisOrder='row-major')

        self.plotTypeMenu = DropDownMenu(options=["Waveform", "FFT", "Spectrogram"], onChoose=self.reloadPlot, firstSelected=True)
        self.xAxisScale = DropDownMenu(options=["Linear X", "Log X"], onChoose=self.reloadPlot, firstSelected=True)
        self.yAxisScale = DropDownMenu(options=["Linear Y", "Log Y"], onChoose=self.reloadPlot, firstSelected=True)

        self.plotTypeMenu.hide()
        self.xAxisScale.hide()
        self.yAxisScale.hide()

        if plotTypeMenu:
            self.plotTypeMenu.show()
        if scaleMenu:
            self.xAxisScale.show()
            self.yAxisScale.show()

        self.settingsDialog = SettingsDialog(on_apply=self.redraw)

        self.addonsMenu = AddonsMenu(onChoose=self.onAddonSelected, dataGetter=self.getAddonData, addons=[
            FindPeaksAddon(),
        ])

        self.addonsMenu.hide()
        if addonsMenu:
            self.addonsMenu.show()

        self.plotLayout = pg.GraphicsLayoutWidget()
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)

        
        self.histogramPlot = pg.HistogramLUTWidget(gradientPosition="left")
        self.histogramPlot.setMinimumWidth(180)
        self.histogramPlot.hide()
        self.histogramPlot.sigLevelChangeFinished.connect(self.histogramLevelsChanged)

        # self.histogramPlot.setMaximumWidth(navHeight)
        self.waveformPlot2.setMaximumHeight(navHeight)

        self.data = None        # x, y
        self.addonData = {}   
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

        self.settingsBtn = Button("Settings", on_click = self.settingsDialog.exec )
        self.settingsBtn.hide()
        if settingsBtn:
            self.settingsBtn.show()

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.plotTypeMenu)
        hlayout.addWidget(self.xAxisScale)
        hlayout.addWidget(self.yAxisScale)
        hlayout.addSpacing(20)
        hlayout.addWidget(self.settingsBtn)
        hlayout.addSpacing(20)
        hlayout.addWidget(self.addonsMenu)
        hlayout.addStretch(1)
        hlayout.addWidget(Button("Autoscale", on_click=self.autoRange))
        plotsHLayout = QHBoxLayout()
        plotsHLayout.addWidget(self.plotLayout)
        plotsHLayout.addWidget(self.histogramPlot)

        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addLayout(plotsHLayout)
        self.setLayout(layout)        
    

    def getViewRangeX(self):
        minX, maxX = self.waveformPlot1.vb.viewRange()[0]
        return minX, maxX
    

    def getAddonData(self):
        if self.addonData == {}:
            return None, self.waveformPlot1, self.waveformPlot2
        minX, maxX = self.waveformPlot1.vb.viewRange()[0]
        minY, maxY = self.waveformPlot1.vb.viewRange()[1]

        self.redraw()

        if self.plotTypeMenu.selected in ["Waveform", "FFT"]:
            x, y = self.addonData["data"]
            x = np.array(x)
            y = np.array(y)
            mask = (x >= minX) & (x <= maxX)
            xvis = x[mask]
            yvis = y[mask]
            self.addonData["visibleData"] = (xvis, yvis)
            self.addonData["viewRangeX"] = [minX, maxX]
            self.addonData["viewRangeY"] = [minY, maxY]
            return self.addonData, self.waveformPlot1, self.waveformPlot2
        
        elif self.plotTypeMenu.selected == "Spectrogram":
            f, t, Sxx = self.addonData["data"]
            maskT = (t >= minX) & (t <= maxX)
            maskF = (f >= minY) & (f <= maxY)
            tvis = t[maskT]
            fvis = f[maskF]
            Sxxvis = Sxx[maskF, :][:, maskT]
            self.addonData["visibleData"] = (fvis, tvis, Sxxvis)
            self.addonData["viewRangeX"] = [minX, maxX]
            self.addonData["viewRangeY"] = [minY, maxY]
            return self.addonData, self.waveformPlot1, self.waveformPlot2


    def onAddonSelected(self, addon):
        # get the visible data from the waveformPlot1
        print(f"Addon selected: {addon.title}")
        addon.exec()


    def reloadPlot(self, _=None, __=None, clear=True):
        ''' Plot with the same data '''
        # print("reloadPlot")
        if self.data is None:
            return
        x, y = self.data
        self.plot(x, y, clear=clear)


    def redraw(self, _=None, __=None, clear=True):
        ''' Plot with the same data without changing the view or the scale '''
        # print("redraw")
        if clear:
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

    def plotInfiniteLine(self, y, color='w', width=2, style=Qt.DashLine):
        infLine = pg.InfiniteLine(pos=y, angle=0, pen=pg.mkPen(color, width=width, style=style))
        self.waveformPlot1.addItem(infLine)

    def plotEnvelope(self, x, y0, y1, clear=True):
        if clear:
            self.clear()
        self.waveformPlot1.plot(x, y0, pen=(255, 0, 0), fillLevel=0, fillBrush=(255, 0, 0, 50))
        self.waveformPlot1.plot(x, y1, pen=(255, 0, 0), fillLevel=0, fillBrush=(255, 0, 0, 50))
        self.waveformPlot2.plot(x, y0, pen=(255, 0, 0), fillLevel=0, fillBrush=(255, 0, 0, 50))
        self.waveformPlot2.plot(x, y1, pen=(255, 0, 0), fillLevel=0, fillBrush=(255, 0, 0, 50))

        self.waveformPlot1.setLabel('bottom', "Time", units='s')
        self.waveformPlot2.setLabel('bottom', "Time", units='s')



    def plot(self, x, y, subsampling=1, clear=True):
        # print("plot")
        if len(x) == 0 or len(y) == 0:
            # print("No data to plot")
            return
        # save the data

        subsampling = int(subsampling)
        if subsampling > 1:
            x = x[::subsampling]
            y = y[::subsampling]

        self.data = x, y

        Ts = x[1] - x[0]    # sampling interval
        if clear:
            self.clear()

        x, y = self.setPadding(x, y, Ts)
        x, y = self.computePlotData(x, y, Ts)
        self.updateLabels()
        self.plotComputedData(x, y)
        self.autoRange()
        self.updateScale()


    def autoRange(self):
        # print("autoRange")
        self.waveformPlot1.autoRange()
        self.waveformPlot2.autoRange()
        self.histogramPlot.autoHistogramRange()
        if self.histDefaultLevels is not None:
            self.histogramPlot.setLevels(*self.histDefaultLevels)
            # print(f"autoRange histDefaultLevels: {self.histDefaultLevels}")
        self.updateRegion(self.waveformPlot1.getViewBox(), self.waveformPlot1.getViewBox().viewRange())


    def plotComputedData(self, x, y):
        # print("plotComputedData")
        if self.plotTypeMenu.selected in ["Waveform", "FFT"]:
            self.waveformPlot1.plot(x, y)
            self.waveformPlot2.plot(x, y)
        elif self.plotTypeMenu.selected == "Spectrogram":
            self.waveformPlot2.plot(x, y)


    def updateScale(self):
        # print("updateScale")
        xlog = True if self.xAxisScale.selected == "Log X" else False
        ylog = True if self.yAxisScale.selected == "Log Y" else False
        plotType = self.plotTypeMenu.selected
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
        # print("computePlotData")
        plotType = self.plotTypeMenu.selected
        if plotType == "FFT":
            # apply the window function
            window = self.settingsDialog["FFTWindow"]
            y = y * signal.get_window(window, len(y))
            y = np.abs(np.fft.rfft(y)) / len(y)
            x = np.fft.rfftfreq(len(x), d=Ts)
            self.addonData = {
                "data": (x, y),
                "type": "FFT",
            }
        elif plotType == "Waveform":
            pass
            self.addonData = {
                "data": (x, y),
                "type": "Waveform",
            }
        elif plotType == "Spectrogram":
            nperseg = int(self.settingsDialog["nperseg"])
            noverlap = int(self.settingsDialog["noverlap"])
            if noverlap >= nperseg:
                noverlap = nperseg - 10
            window = self.settingsDialog["specWindow"]
            f, t, Sxx = signal.spectrogram(y, fs=1/Ts, nperseg=nperseg, noverlap=noverlap, scaling='spectrum', mode='magnitude')

            if self.yAxisScale.selected == "Log Y":
                Sxx = np.log10(Sxx)

            self.addonData = {
                "data": (f, t, Sxx),
                "type": "Spectrogram",    
            }

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
        # print("updateLabels")
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
        padding = int(self.settingsDialog["padding"])
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
        # print(f"histogramLevelsChanged: {self.histLastLevels}")