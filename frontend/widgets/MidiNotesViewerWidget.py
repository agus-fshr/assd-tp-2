from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QProgressBar, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, Qt

import pyqtgraph as pg

import numpy as np
from scipy import signal

from .BasicWidgets import DropDownMenu, Button, TextInput, Slider
# from .DynamicSettingsWidget import DynamicSettingsWidget
# from backend.utils.ParamObject import ParameterList, NumParam, TextParam, BoolParam, ChoiceParam

class CustomPlotWidget(pg.PlotWidget):
    clicked = pyqtSignal()

    def wheelEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        print("Mouse press")
        self.clicked.emit()
        event.ignore()



class SynthTrackPopup(QDialog):
    closed = pyqtSignal(int)
    def __init__(self, parent=None, track_name="No track", model=None, notes=None):
        super().__init__(parent)
        self.setWindowTitle("Sintetizar " + track_name)
        self.track_name = track_name
        self.model = model
        self.notes = notes
        self.progress = 0
        self.layout = QVBoxLayout()
        self.initUI(self.layout)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        # self.cancel_synth()
        self.closed.emit(self.progress)
        super().closeEvent(event)

    def showEvent(self, event):
        self.resize(400, 200)  # w, h               # Set size of the QDialog
        # self.move(100, 100)  # X, Y                 # Set position of the QDialog
        # set the position of the dialog in the center of the screen
        self.move(500, 500)
        self.setModal(True)         # Set the dialog to be modal (block the parent window)
        super().showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
            if self.on_apply is not None:
                self.on_apply()
        else:
            super().keyPressEvent(event)

    def load_instrument_options(self):
        options = {}
        for instrument in self.model.synthesizers:
            options[instrument.name] = instrument
        self.instrumentSelector.set_options(options, firstSelected=True)

    def load_effect_options(self):
        options = {}
        for effect in self.model.effects:
            options[effect.name] = effect
        self.effectSelector.set_options(options, firstSelected=True)

    def load_options(self, selector, elements):
        options = {}
        for e in elements:
            options[e.name] = e
        selector.set_options(options, firstSelected=True)

    def begin_synth(self):
        instrument = self.instrumentSelector.selected
        effect = self.effectSelector.selected
        self.model.synthTrackManager.synthesize_track(self.track_name, instrument, self.notes, self.volume.value(), effect)
        self.model.synthTrackManager.progressUpdate.connect(self.update_progress)
        self.model.synthTrackManager.synthTrackComplete.connect(self.synth_complete)
        self.progressBar.show()

    def synth_complete(self, trackName, track_data):
        try:
            self.model.synthTrackManager.progressUpdate.disconnect(self.update_progress)
            self.model.synthTrackManager.synthTrackComplete.disconnect(self.synth_complete)
        except:
            pass
        self.model.audioPlayer.set_array(track_data["track_array"])
        self.progressBar.hide()
        self.accept()

    def update_progress(self, value):
        self.progressBar.setValue(value)
        self.progress = value

    def cancel_synth(self):
        print("Cancelling synth")
        self.model.synthTrackManager.cancel()
        self.progressBar.hide()
        self.close()


    def initUI(self, layout):
        titleLabel = QLabel(f"Sintetizar '{self.track_name}'")
        titleLabel.setFont(QFont("Arial", 16))
        layout.addSpacing(10)
        layout.addWidget(titleLabel)
        layout.addSpacing(10)

        synth_tools = QHBoxLayout()
        self.instrumentSelector = DropDownMenu("Select Instrument", onChoose=lambda name, obj: None)
        self.effectSelector = DropDownMenu("Select Effect", onChoose=lambda name, obj: None)
        self.volume = Slider("Volume", interval=(0.01, 1.0), step=0.01, defaultVal=1.0)
        self.load_options(self.instrumentSelector, self.model.synthesizers)
        self.load_options(self.effectSelector, self.model.effects)
        synth_tools.addWidget(self.instrumentSelector)
        synth_tools.addWidget(self.effectSelector)
        layout.addLayout(synth_tools)
        layout.addWidget(self.volume)

        layout.addSpacing(20)

        beginBtn = Button("Comenzar", background_color="lightgreen")
        beginBtn.clicked.connect(self.begin_synth)
        cancelBtn = Button("Detener", background_color="lightcoral")
        cancelBtn.clicked.connect(self.cancel_synth)

        layout.addSpacing(20)

        self.progressBar = QProgressBar()
        self.progressBar.setFixedHeight(20)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.hide()

        layout.addWidget(beginBtn)
        layout.addWidget(cancelBtn)
        layout.addSpacing(20)
        layout.addWidget(self.progressBar)





class MidiNotesViewerWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, track_name, model, notes, trackHeight=200):
        super().__init__()

        self.popup = SynthTrackPopup(self, track_name, model, notes)
        self.popup.hide()
        self.popup.closed.connect(self.popup_closed)
        self.model = model

        self.plotWidget = CustomPlotWidget()
        self.plotWidget.clicked.connect(self.on_click)
        self.plotWidget.setMouseTracking(False)
        self.plotItem = self.plotWidget.getPlotItem()
        self.plotWidget.setLabel('bottom', "Time", units='s')
        self.plotWidget.setLabel('left', "Note")
        self.plotWidget.setBackground(None)
        self.plotItem.vb.setMouseEnabled(y=False, x=False)
        self.plotItem.vb.setMouseMode(pg.ViewBox.PanMode)

        self.plotWidget.setFixedHeight(trackHeight)

        layout = QVBoxLayout()
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)        

        self.plotNotes(notes)
    
    def popup_closed(self, progress):
        pass

    def on_click(self):
        if not self.model.synthTrackManager.is_busy():
            self.popup.show()
            self.popup.move(self.mapToGlobal(self.rect().center()))
        self.clicked.emit()


    def plotNotes(self, notes):
        self.plotItem.clear()

        x = [n.time_on for n in notes]  # Start times
        height = [1 for _ in notes]     # Heights (all 1)
        width = [n.time_off - n.time_on for n in notes]  # Widths
        y = [n.note for n in notes]     # MIDI note numbers
        
        min_note = np.min(y)
        max_note = np.max(y)

        if max_note - min_note < 10:
            self.plotItem.setYRange(min_note - 5, max_note + 5)

        # Create a bar graph item
        bargraph = pg.BarGraphItem(x=x, height=height, width=width, y=y, brush='r')
        self.plotItem.addItem(bargraph)
