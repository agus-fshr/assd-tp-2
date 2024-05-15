from PyQt5.QtCore import pyqtSignal, QObject
from backend.utils.Worker import Worker

import numpy as np

class SynthTrackManager(QObject):
    errorOccurred = pyqtSignal(str)
    progressUpdate = pyqtSignal(int)
    synthTrackComplete = pyqtSignal(str, dict)

    def __init__(self, framerate):
        super().__init__()
        self.framerate = framerate        
        self.worker = None
        self.synth_track_data = None
        self.track_array = None
        self.sending_progress = False

    @staticmethod
    def synthWorkerFunction(n0, note, amplitude, duration, instrument, effect=None):
        wave_array = instrument(note, amplitude, duration)
        if effect is not None:
            wave_array = effect(wave_array)
        return n0, wave_array
    

    def is_busy(self):
        return self.worker is not None and self.worker.isRunning()
    

    def synthesize_track(self, trackName, instrument, note_array, volume, effect=None):

        # OUTPUT
        self.synth_track_data = {
            "description": "Write description here",
            "track_array": None,
            "instrument": instrument.name,
            "effect": effect.name if effect is not None else "None",
            "framerate": self.framerate,
        }

        self.worker = Worker(function=self.synthWorkerFunction, task_key=trackName)

        total_song_frames = int(note_array[-1].duration * self.framerate)
        timeLimiter = 9999.0
        lastTime = 0.0
        n0 = 0
        for note in note_array:
            # d = n.time_on - lastTime
            # lastTime = n.time_on
            delay = note.time_on - lastTime
            lastTime = note.time_on

            if note.time_off is not None and note.time_off > timeLimiter:
                print("Reached time limit!")
                break

            amp = note.amplitude * volume
            
            total_song_frames += int(delay * 1.01 * self.framerate)

            n0 += int(delay * self.framerate)
            self.worker.add_task((n0, note.note, amp, note.duration, instrument, effect))


        # print(f"Song Length (Samples): {total_song_frames}")
        
        self.track_array = np.zeros(total_song_frames + self.framerate * 1)


        self.worker.taskComplete.connect(self.on_note_synthesized)
        self.worker.finished.connect(self.on_track_synthesized)
        self.worker.onError.connect(self.errorOccurred)

        self.sending_progress = True
        self.worker.start()


    def cancel(self):
        if self.worker is not None:
            self.sending_progress = False
            self.worker.cancel()
            self.worker.wait()


    def on_note_synthesized(self, note_synth_pack):
        n0, wave_array = note_synth_pack
        try:
            if n0 + wave_array.size >= self.track_array.size:
                # print("ERROR: Song too short or note too long. Adding more zeros to wave_array")
                zeros_needed = n0 + wave_array.size - self.track_array.size + 1  # +1 to avoid off-by-one error
                self.track_array = np.append(self.track_array, np.zeros(zeros_needed))
                return

            self.track_array[n0 : n0 + wave_array.size] += wave_array

            if self.sending_progress:
                self.progressUpdate.emit(self.worker.progress())

        except Exception as e:
            print(__file__, '\t', e)
            self.errorOccurred.emit(str(e))
            self.synthWorker.cancel()
            self.synthWorker.wait()
            return


    def on_track_synthesized(self, track_name):
        
        self.synth_track_data["track_array"] = self.track_array
        self.synthTrackComplete.emit(track_name, self.synth_track_data)

        self.sending_progress = False
        self.synth_track_data = None
        self.track_array = None
        self.worker = None