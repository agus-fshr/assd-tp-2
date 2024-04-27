
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget, QSlider, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QSizePolicy
from PyQt5.QtGui import QColor, QPalette, QFont

from .BasicWidgets import Button, SwitchButton

class ClickableSlider(QSlider):
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
    def __init__(self, audioPlayer):
        super().__init__()
        self.audioPlayer = audioPlayer
        self.audioPlayer.errorOccurred.connect(self.on_error)
        self.audioPlayer.finished.connect(self.on_finished)
        self.audioPlayer.currentTimeUpdated.connect(self.audio_player_frame_changed)

        # Add border to the widget
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        # Create a QHBoxLayout to arrange the widgets horizontally
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.initUI(layout)
        self.setLayout(layout)
    
    def initUI(self, layout):
        self.playPauseButton = Button("Play", on_click=self.toggle_button_callback)
        # self.playPauseButton = SwitchButton("Pause", "Play", on_click=self.toggle_button_callback, background_color_on="white", background_color_off="white", color_on="black", color_off="black")
        # self.playPauseButton.set_value(False)
        
        # self.playButton = Button("Play", on_click=self.play)
        # self.pauseButton = Button("Pause", on_click=self.pause)
        self.stopButton = Button("Stop", on_click=self.audioPlayer.stop)

        self.timeLabel = QLabel("0:00.00 / 0:00.00")
        self.timeLabel.setFont(QFont("Arial", 12))

        self.slider = ClickableSlider(Qt.Horizontal)

        # set a custom style for the slider groove and handle
        self.set_slider_style()

        self.slider.setRange(0, 0)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.slider.sliderReleased.connect(self.slider_released)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider.clicked.connect(self.mouse_press_event)
        

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.playPauseButton)
        # btnLayout.addWidget(self.pauseButton)
        btnLayout.addWidget(self.stopButton)
        btnLayout.addWidget(self.timeLabel)
        btnLayout.addStretch(1)
        btnLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        
        layout.addWidget(self.slider)
        layout.addLayout(btnLayout)
        # layout.addStretch(1)

    def audio_player_frame_changed(self, frame):
        self.slider.setValue(frame)

    def slider_value_changed(self, value):
        self.set_time_label(value)

    def mouse_press_event(self, sliderPos):
        self.audioPlayer.seek(sliderPos)
        self.slider.setValue(sliderPos)

    def slider_pressed(self):
        self.slider.setRange(0, self.audioPlayer.nframes)
        self.audioPlayer.pause()

    def slider_released(self):
        frame = self.slider.value()
        self.audioPlayer.seek(frame)

    def set_time_label(self, frame):
        current = self.audioPlayer.frames_to_pretty_time_str(frame)
        total = self.audioPlayer.frames_to_pretty_time_str(self.audioPlayer.nframes)
        self.timeLabel.setText(f"{current} / {total}")

    def toggle_button_callback(self):
        if self.audioPlayer.isRunning():
            if self.pause():
                self.playPauseButton.setText("Play")
        else:
            if self.play():
                self.playPauseButton.setText("Pause")

    def play(self):
        self.slider.setRange(0, self.audioPlayer.nframes)
        self.slider.setEnabled(True)
        return self.audioPlayer.play()

    def pause(self):
        return self.audioPlayer.pause()

    def stop(self):
        self.audioPlayer.stop()
    
    def on_error(self, error):
        QMessageBox.critical(self, 'Error', str(error))
    
    def on_finished(self):
        self.slider.setValue(0)
        self.playPauseButton.setText("Play")


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














        