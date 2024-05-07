
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget, QSlider, QFrame, QTimeEdit
from PyQt5.QtCore import Qt, pyqtSignal, QTime
from PyQt5.Qt import QSizePolicy
from PyQt5.QtGui import QColor, QPalette, QFont

from .BasicWidgets import Button, SwitchButton

class ClickableSlider(QSlider):
    # pass
    clicked = pyqtSignal(int)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x() - 10
            w = self.width() - 20
            start = self.minimum()
            end = self.maximum()
            sliderPos = start + (end - start) * x // w
            sliderPos = min(end, max(start, sliderPos))
            self.clicked.emit(sliderPos)
        super().mousePressEvent(event)


class AudioPlayerWidget(QFrame):
    # _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(AudioPlayerWidget, cls).__new__(cls)
    #     return cls._instance

    def __init__(self, audioPlayer):
        super().__init__()
        # if not hasattr(self, 'initialized') or not self.initialized:
        if True:
            self.audioPlayer = audioPlayer

            # Add border to the widget
            self.setFrameStyle(QFrame.Panel | QFrame.Raised)

            # Create a QHBoxLayout to arrange the widgets horizontally
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.initUI(layout)
            self.setLayout(layout)

        #     self.initialized = True
        # else:
        #     self.audioPlayer = audioPlayer
        #     self.audioPlayer.errorOccurred.connect(self.audio_player_error)
        #     self.audioPlayer.finished.connect(self.audio_player_finished)
        #     self.audioPlayer.currentTimeUpdated.connect(self.audio_player_frame_changed) 
    
    def initUI(self, layout):
        self.playPauseButton = Button("Play", on_click=self.toggle_button_callback)

        self.stopButton = Button("Stop", on_click=self.audioPlayer.stop)

        self.slider = ClickableSlider(Qt.Horizontal)

        # set a custom style for the slider groove and handle
        self.set_slider_style()

        self.slider.setRange(0, 0)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.slider.sliderReleased.connect(self.slider_released)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider.clicked.connect(self.mouse_press_event)
        

        self.timeLabel = QTimeEdit()
        self.timeLabel.setDisplayFormat("mm:ss.zzz")
        self.timeLabel.setReadOnly(True)
        self.timeLabel.setButtonSymbols(QTimeEdit.NoButtons)
        self.timeLabel.setFont(QFont("Arial", 12))
        self.totalTimeLabel = QLabel("/ 00:00.000")
        self.totalTimeLabel.setFont(QFont("Arial", 12))

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.playPauseButton)
        btnLayout.addWidget(self.stopButton)
        btnLayout.addSpacing(20)
        btnLayout.addWidget(self.timeLabel)
        btnLayout.addWidget(self.totalTimeLabel)
        btnLayout.addStretch(1)
        btnLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        
        layout.addWidget(self.slider)
        layout.addLayout(btnLayout)


    def slider_value_changed(self, value):
        if value == 0:
            print("slider = 0")
        self.set_time_label(value)

    def set_time_label(self, frame):
        current = self.audioPlayer.frames_to_pretty_time_str(frame)
        time = QTime.fromString(current, "mm:ss.zzz")
        self.timeLabel.setTime(time)
        self.timeLabel.update()

    def audio_player_frame_changed(self, frame):
        self.slider.setValue(frame)

    def mouse_press_event(self, sliderPos):
        self.slider.setValue(sliderPos)

    def slider_pressed(self):
        print("slider pressed")
        self.disconnectEvents()
        self.slider.setRange(0, self.audioPlayer.nframes)
        self.audioPlayer.pause()
        self.playPauseButton.setText("Play")

    def slider_released(self):
        print("slider released")
        frame = self.slider.value()
        self.audioPlayer.seek(frame)
        self.connectEvents()


    def toggle_button_callback(self):
        if self.audioPlayer.isPlaying():
            self.pause()
            self.playPauseButton.setText("Play")
        else:
            if self.audioPlayer.willPlay():
                self.playPauseButton.setText("Pause")
                self.play()

    def play(self):
        print("play")
        self.slider.setRange(0, self.audioPlayer.nframes)
        self.slider.setEnabled(True)
        self.connectEvents()

        totalTime_str = self.audioPlayer.frames_to_pretty_time_str(self.audioPlayer.nframes)
        self.totalTimeLabel.setText(f"/ {totalTime_str}")
        self.audioPlayer.play()


    def pause(self):
        print("pause")
        self.audioPlayer.pause()
        self.disconnectEvents()


    def stop(self):
        print("stop")
        self.audioPlayer.stop()
        self.disconnectEvents()
        self.playPauseButton.setText("Play")
        self.slider.setValue(0)

    
    def audio_player_error(self, error):
        QMessageBox.critical(self, 'Error', str(error))
        
    
    def audio_player_finished(self):
        print("audio player finished")
        self.disconnectEvents()
        self.playPauseButton.setText("Play")
        self.slider.setValue(0)


    def connectEvents(self):
        self.audioPlayer.errorOccurred.connect(self.audio_player_error)
        self.audioPlayer.finished.connect(self.audio_player_finished)
        self.audioPlayer.currentTimeUpdated.connect(self.audio_player_frame_changed)

    def disconnectEvents(self):
        try:
            self.audioPlayer.errorOccurred.disconnect(self.audio_player_error)
            self.audioPlayer.finished.disconnect(self.audio_player_finished)
            self.audioPlayer.currentTimeUpdated.disconnect(self.audio_player_frame_changed)
        except TypeError:
            pass


    def set_slider_style(self):
        # Set the slider handle color to the primary color
        handle_color = self.palette().color(QPalette.Highlight).name()
        bar_color = self.palette().color(QPalette.ColorRole.Highlight)
        bar_color = QColor.fromHsv(bar_color.hue(), bar_color.saturation() // 2, bar_color.value() ).name()
        # bar_color = "lightblue"
        bar_color = "lightgrey"
        self.slider.setStyleSheet(f""" 
            QSlider::groove:horizontal {{
                border: 1px solid #bbb;
                background: lightgrey;
                height: 10px;
                border-radius: 5px;
            }}
                                    
            QSlider::handle:horizontal {{
                background: transparent;
                width: 18px;
                margin: -4px 0; 
                border-radius: 5px;
                border: 1px solid transparent;
            }}
                                    
            QSlider::handle:horizontal:disabled {{
                width: 18px;
                margin: -4px 0; 
                background: transparent;
                border: 1px solid transparent;
            }}

            QSlider::handle:horizontal:hover {{
                width: 18px;
                margin: -4px 0; 
                background: {handle_color};
                border: 1px solid #777;
            }}

            QSlider::handle:horizontal:pressed {{
                width: 18px;
                margin: -4px 0; 
                background: lightgrey;
                border: 1px solid #777;
            }}

            QSlider::sub-page:horizontal {{
                background: {handle_color};
                border-radius: 5px;
            }}
        """)














        