from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget

import pyqtgraph as pg

class WaveformViewerWidget(QWidget):
    def __init__(self, navHeight=100):
        super().__init__()

        self.plotLayout = pg.GraphicsLayoutWidget(show=True)
        self.waveformPlot1 = self.plotLayout.addPlot(row=1, col=0)
        self.waveformPlot2 = self.plotLayout.addPlot(row=2, col=0)
        self.waveformPlot2.setMaximumHeight(navHeight)
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

        layout = QVBoxLayout()
        layout.addWidget(self.plotLayout)
        self.setLayout(layout)


    def plot(self, x, y):

        self.waveformPlot1.clear()
        self.waveformPlot2.clear()
        self.waveformPlot2.addItem(self.region, ignoreBounds=True)
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