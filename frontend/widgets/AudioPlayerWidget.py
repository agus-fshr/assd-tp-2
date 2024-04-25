
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget
from PyQt5.QtCore import Qt

from .BasicWidgets import Button, SwitchButton

class AudioPlayerWidget(QWidget):
    def __init__(self, audioPlayer):
        super().__init__()
        self.audioPlayer = audioPlayer
        self.audioPlayer.errorOccurred.connect(self.on_error)
        self.audioPlayer.finished.connect(self.on_finished)

        # Create a QHBoxLayout to arrange the widgets horizontally
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.initUI(layout)
        self.setLayout(layout)
    
    def initUI(self, layout):
        self.playButton = Button("Play", on_click=self.audioPlayer.play)
        self.pauseButton = Button("Pause", on_click=self.audioPlayer.pause)
        self.stopButton = Button("Stop", on_click=self.audioPlayer.stop)

        layout.addWidget(self.playButton)
        layout.addWidget(self.pauseButton)
        layout.addWidget(self.stopButton)
        layout.addStretch(1)
    
    
    def on_error(self, error):
        QMessageBox.critical(self, 'Error', str(error))
    
    def on_finished(self):
        pass