from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QDialog, QLabel, QSpinBox
from PyQt5.QtGui import QTransform
from PyQt5.QtCore import pyqtSignal, Qt

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput
from .DynamicSettingsWidget import DynamicSettingsWidget
from backend.utils.ParamObject import ParameterList, NumParam, TextParam, BoolParam, ChoiceParam


class MidiNotesViewerWidget(QWidget):
    def __init__(self, trackHeight=100, onFFT = lambda f, x: None, onEvent = None):
        super().__init__()

        self.plotItem = pg.PlotItem()
        self.plotItem.setLabel('bottom', "Time", units='s')
        self.plotItem.vb.setMouseEnabled(y=False, x=False)
        self.plotItem.setMaximumHeight(trackHeight)

        layout = QVBoxLayout()
        layout.addWidget(self.plotItem)
        self.setLayout(layout)        
    

    def plot(self, notes):
        self.plotItem.clear()
        for n in notes:
            t0 = n.time_on      # Start time [s]
            t1 = n.time_off     # End time [s]
            note = n.note       # MIDI note number [0, 127]

        # Create a rectangle for the note
        rect = pg.QtGui.QGraphicsRectItem(t0, note, t1-t0, 1)
        rect.setBrush(pg.mkBrush('r'))
        rect.setPen(pg.mkPen('r'))
        rect.setZValue(10)
        self.plotItem.addItem(rect)
