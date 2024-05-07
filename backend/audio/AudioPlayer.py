from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker
from PyQt5 import QtCore
from PyQt5 import Qt
import pyaudio
import numpy as np
import wave
import io
import time

import platform
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    if platform.system() == 'Linux':
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    else:
        yield

# # After doing this you can re-use the error handler by using the noalsaerr context:

# with noalsaerr():
#     p = pyaudio.PyAudio()
# stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)


class AudioPlaybackThread(QThread):
    errorOccurred = pyqtSignal(str)
    currentTimeUpdated = pyqtSignal(int)  # Emit the current play time in frames
    finished = pyqtSignal()

    def __init__(self, wave_obj, chunk_size=2048):
        super().__init__()
        self.wo = wave_obj
        self.is_paused = False
        self.is_stopped = False
        self.mutex = QMutex()
        self.total_frames_read = 0
        self.paused_at_frame = 0
        self.chunk_size = chunk_size

    def run(self):
        with noalsaerr():
            p = pyaudio.PyAudio()
    
        stream = None
        data = None
        try:
            stream = p.open(format=p.get_format_from_width(self.wo.getsampwidth()),
                            channels=self.wo.getnchannels(),
                            rate=self.wo.getframerate(),
                            output=True,
                            frames_per_buffer=self.chunk_size)
            
            self.wo.setpos(self.total_frames_read)

            bytes_per_frame = self.wo.getsampwidth() * self.wo.getnchannels()
            
            data = self.wo.readframes(self.chunk_size)
            while data and not self.is_stopped:
                stream.write(data)

                # Calculate the current TIME in frames
                self.total_frames_read += len(data) // bytes_per_frame
                
                data = self.wo.readframes(self.chunk_size)

                self.currentTimeUpdated.emit(self.total_frames_read)
                with QMutexLocker(self.mutex):
                    if self.is_paused or self.is_stopped:
                        # print("BREAK")
                        break

        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()

            if self.is_stopped or data is None or len(data) == 0:
                # print("FINISHED")
                self.wo.rewind()
                self.finished.emit()
                self.total_frames_read = 0
                self.currentTimeUpdated.emit(self.total_frames_read)


    def seek(self, frame_index):
        with QMutexLocker(self.mutex):
            try:
                self.wo.setpos(frame_index)
                self.total_frames_read = frame_index
                self.currentTimeUpdated.emit(self.total_frames_read)
                # Force pause after seeking
                self.is_paused = True
                self.paused_at_frame = frame_index
            except Exception as e:
                self.errorOccurred.emit(f"AudioPlayback seek error: {str(e)}")


    def isPaused(self):
        return self.is_paused

    def pause(self):
        print(f"\tPausing {self.total_frames_read}")
        # with QMutexLocker(self.mutex):
        #     self.is_paused = True
        self.paused_at_frame = self.total_frames_read
        with QMutexLocker(self.mutex):
            self.is_paused = True


    def start(self):
        if self.is_paused:
            self.total_frames_read = self.paused_at_frame
        print(f"\tStarting {self.total_frames_read}")
        with QMutexLocker(self.mutex):
            self.is_stopped = False
            self.is_paused = False
        super().start()

    def stop(self):
        print(f"\tStopping {self.total_frames_read}")
        with QMutexLocker(self.mutex):
            self.is_stopped = True
            self.is_paused = False  # Ensure the thread exits if it was paused



class TimeUpdatingThread(QThread):
    timeUpdated = pyqtSignal(int)  # Emit the current play time in frames

    def __init__(self, audio_player):
        super().__init__()
        self.audio_player = audio_player
        self.last_frame = 0
        self.is_stopped = False

    def run(self):
        self.is_stopped = False
        print(f"\trun TimeUpdatingThread: {self.audio_player.current_frame}")
        while not self.is_stopped:
            # Read from current_frame
            if self.last_frame != self.audio_player.current_frame:
                self.last_frame = self.audio_player.current_frame
                self.timeUpdated.emit(self.last_frame)

            time.sleep(0.05)  # Sleep for a short time to reduce CPU usage

    def stop(self):
        print(f"\tstop TimeUpdatingThread: {self.audio_player.current_frame}")
        self.is_stopped = True



class AudioPlayer(QObject):
    
    finished = pyqtSignal()
    errorOccurred = pyqtSignal(str)    
    currentTimeUpdated = pyqtSignal(int)  # Emit the current play time in frames

    current_frame = 0

    playback_thread = None
    nframes = 0
    framerate = 44100

    def __init__(self):
        super().__init__()
        self.emit_time_thread = TimeUpdatingThread(self)
        self.emit_time_thread.timeUpdated.connect(self.currentTimeUpdated)

    def isPlaying(self):
        if self.playback_thread is None:
            return False
        return self.playback_thread.isRunning() and not self.playback_thread.isPaused()

    def willPlay(self):
        if self.playback_thread is None:
            return False
        return (not self.playback_thread.isRunning()) or self.playback_thread.isPaused()


    def play(self):
        if self.playback_thread is None:
            return

        if not self.playback_thread.isRunning():
            self.playback_thread.start()
            self.emit_time_thread.start()
        elif self.playback_thread.isPaused():
            self.playback_thread.resume()
            self.emit_time_thread.start()


    def pause(self):
        if self.playback_thread:
            self.emit_time_thread.stop()
            self.playback_thread.pause()
            self.emit_time_thread.wait()  # Wait for the thread to finish
            self.playback_thread.wait()  # Wait for the thread to finish


    def stop(self):
        if self.playback_thread:
            self.emit_time_thread.stop()
            self.playback_thread.stop()
            self.emit_time_thread.wait()  # Wait for the thread to finish
            self.playback_thread.wait()  # Wait for the thread to finish
    

    def seek(self, frame_index):
        if self.playback_thread:
            self.emit_time_thread.stop()
            self.playback_thread.seek(frame_index)


    def update_current_playback_time(self, frame_index):
        self.current_frame = frame_index


    def frames_to_pretty_time_str(self, frames):
        total_seconds = frames // self.framerate
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        second_fraction = (frames % self.framerate) // (self.framerate // 1000)

        return f"{minutes:02d}:{seconds:02d}.{second_fraction:03d}"


    # NO TOCAR ESTO !!!     DO NOT TOUCH THIS !!!
    def set_array(self, np_array, framerate=44100, channels=1):
        # Scale the numpy array to the range of np.int16
        np_array = np.clip(np_array, -1.0, 1.0)
        np_array = np.int16(np_array * 32767)
        
        # Convert the numpy array to bytes
        byte_data = np_array.tobytes()
        
        # Create a new wave file in memory
        io_data = io.BytesIO()
        with wave.open(io_data, 'wb') as wo:
            wo.setnchannels(channels)
            wo.setsampwidth(2)  # 2 bytes for np.int16
            wo.setframerate(framerate)
            wo.writeframes(byte_data)
        
        # Reset the buffer's file position to the beginning
        io_data.seek(0)

        # Return the wave object
        self.set_wave_object(wave.open(io_data, 'rb'))


    def set_from_file(self, file_path):
        try:
            self.set_wave_object(wave.open(file_path, 'rb'))
        except Exception as e:
            self.errorOccurred.emit(str(e))


    def save_to_file(self, file_path):
        if self.playback_thread is None:
            return

        with wave.open(file_path, 'wb') as wo:
            wo.setnchannels(self.playback_thread.wo.getnchannels())
            wo.setsampwidth(self.playback_thread.wo.getsampwidth())
            wo.setframerate(self.playback_thread.wo.getframerate())
            wo.writeframes(self.playback_thread.wo.readframes(self.nframes))


    def get_numpy_data(self):
        if self.playback_thread is None:
            return None

        # Read all frames from the wave object
        self.playback_thread.wo.rewind()
        arr = np.frombuffer(self.playback_thread.wo.readframes(self.nframes), dtype=np.int16)
        time = np.linspace(0, len(arr) / self.framerate, len(arr))
        return time, np.clip(arr / 32767.0, -1.0, 1.0)


    def set_wave_object(self, wave_obj):
        self.stop()
        
        self.playback_thread = AudioPlaybackThread(wave_obj)
        self.playback_thread.errorOccurred.connect(self.errorOccurred)
        self.playback_thread.currentTimeUpdated.connect(self.update_current_playback_time)
        self.playback_thread.finished.connect(self.finished)

        self.framerate = wave_obj.getframerate()
        self.nframes = wave_obj.getnframes()