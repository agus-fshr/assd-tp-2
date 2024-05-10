from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QScrollArea, QSlider, QFileDialog
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button, TextInput, Slider, DropDownMenu
from frontend.widgets.ConsoleWidget import ConsoleWidget

from frontend.widgets.AudioPlayerWidget import AudioPlayerWidget

from frontend.widgets.WaveformViewerWidget import WaveformViewerWidget

import numpy as np
from scipy import signal


class SoundPlayerPage(BaseClassPage):

    title = "Sound Player"    

    def initUI(self, layout):
        # Class widgets (used externally with self.)
        self.dropDown = DropDownMenu("Select Sound", onChoose=self.on_sound_selected)

        # Local widgets (used only in the initUI method)
        topHLayout = QHBoxLayout()

        # Setup top layout
        topHLayout.addWidget(self.dropDown)
        topHLayout.addStretch(1)

        # Setup audio player widget
        self.playerWidget = AudioPlayerWidget(audioPlayer=self.model.audioPlayer)

        # Setup waveform viewer widget
        self.plotWidget = WaveformViewerWidget(onFFT=self.onFFT, onEvent=self.waveformViewerEvent)
        
        # Add widgets to page layout
        layout.addLayout(topHLayout)
        layout.addSpacing(20)
        layout.addWidget(self.playerWidget)
        layout.addSpacing(20)
        layout.addWidget(self.plotWidget)


    def waveformViewerEvent(self, event):
        if event["type"] == "captureVisibleData":
            x = event["x"]
            y = event["y"]

            dx_mean = 0
            c = 0
            for i in range(1, len(x)):
                dx_mean += x[i] - x[i-1]
                c += 1
            dx_mean /= c

            print(f"f_mean: {1/dx_mean}")

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            default_filename = "data_out.csv"
            filename, _ = QFileDialog.getSaveFileName(self, "Save as TXT", default_filename, "Text Files (*.txt)", options=options)
            if filename:
                # save as TXT
                with open(filename, mode='w') as file:
                    file.write("RIR_2 = np.array([\n")
                    for i in range(len(y)):
                        file.write(f"{y[i]:.4f},")
                    file.write("])\n")

    # Refresh dropdown options looking for newly imported .WAV files
    def refresh_sound_options(self):
        options = {}
        for fmeta in self.model.file_handler.available_files("wav"):
            options[fmeta.name] = fmeta.path
        
        self.dropDown.set_options(options)


    def onFFT(self, f, x):
        # search for peaks
        f_50_hz_distance = int(80 / (f[1] - f[0]))
        peaks = signal.find_peaks(x, height=0.0001, distance=f_50_hz_distance)
        peaks_f = f[peaks[0]]
        peaks_x = x[peaks[0]]
        print(f"size: {len(x)}, max: {max(x)}, min: {min(x)} 50_Hz_dist: {f_50_hz_distance} peaks: {len(peaks_f)}")
        
        # Order peaks by amplitude (from highest to lowest amplitude)
        peaks_f = peaks_f[np.argsort(peaks_x)[::-1]]
        peaks_x = peaks_x[np.argsort(peaks_x)[::-1]]

        print("Peaks:")
        for pf, px in zip(peaks_f, peaks_x):
            print(f"\t{pf:.2f} Hz: {px:.5f}")

        self.plotWidget.scatter(peaks_f, peaks_x)

    # Callback to set the selected sound to play
    def on_sound_selected(self, name, path):
        self.model.audioPlayer.set_from_file(path)

        time, array = self.model.audioPlayer.get_numpy_data()

        self.plotWidget.plot(time, array)


    # Refresh dropdown options looking for new sound files
    def on_tab_focus(self):
        self.refresh_sound_options()
