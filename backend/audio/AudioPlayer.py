from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker, QWaitCondition
import pyaudio
import numpy as np
import wave
import io

class AudioPlaybackThread(QThread):
    errorOccurred = pyqtSignal(str)
    currentTimeUpdated = pyqtSignal(int)  # Emit the current play time in frames
    finished = pyqtSignal()

    def __init__(self, wave_obj):
        super().__init__()
        self.wo = wave_obj
        self.is_paused = False
        self.is_stopped = False
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
        self.total_frames_read = 0

    def run(self):
        p = pyaudio.PyAudio()
        stream = None
        try:
            # chunk_size = 1024
            chunk_size = 2048

            stream = p.open(format=p.get_format_from_width(self.wo.getsampwidth()),
                            channels=self.wo.getnchannels(),
                            rate=self.wo.getframerate(),
                            output=True,
                            frames_per_buffer=chunk_size)
            self.wo.setpos(self.total_frames_read)

            data = self.wo.readframes(chunk_size)
            while data and not self.is_stopped:
                stream.write(data)
                
                # Calculate the current TIME in seconds
                self.total_frames_read += len(data) // self.wo.getsampwidth() // self.wo.getnchannels()
                self.currentTimeUpdated.emit(self.total_frames_read)

                data = self.wo.readframes(chunk_size)
                with QMutexLocker(self.mutex):
                    if self.is_paused:
                        self.pause_condition.wait(self.mutex)  # Wait until resume is called
                    if self.is_stopped:
                        break
        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()
            self.wo.rewind()
            self.finished.emit()
            self.total_frames_read = 0

    def seek(self, frame_index):
        with QMutexLocker(self.mutex):
            # Use setpos() to seek to the desired frame
            try:
                self.wo.setpos(frame_index)
                self.total_frames_read = frame_index
                # Force pause after seeking
                self.is_paused = True
            except Exception as e:
                self.errorOccurred.emit(f"AudioPlayback seek error: {str(e)}")

    def isPaused(self):
        return self.is_paused

    def pause(self):
        with QMutexLocker(self.mutex):
            self.is_paused = True

    def resume(self):
        with QMutexLocker(self.mutex):
            self.is_paused = False
            self.pause_condition.wakeAll()

    def start(self):
        with QMutexLocker(self.mutex):
            self.is_stopped = False
            self.is_paused = False
            self.pause_condition.wakeAll()
        super().start()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_stopped = True
            self.is_paused = False  # Ensure the thread exits if it was paused
            self.pause_condition.wakeAll()  # Wake the thread if it's waiting
        self.wo.rewind()
        self.total_frames_read = 0




class AudioPlayer(QObject):
    finished = pyqtSignal()
    errorOccurred = pyqtSignal(str)
    currentTimeUpdated = pyqtSignal(int)  # Emit the current play time in frames
    
    playback_thread = None
    nframes = 0
    framerate = 44100

    def frames_to_pretty_time_str(self, frames):
        total_seconds = frames // self.framerate
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        second_fraction = (frames % self.framerate) // (self.framerate // 100)

        return f"{minutes}:{seconds:02d}.{second_fraction:02d}"

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
        self.set_wave_object(wave.open(file_path, 'rb'))



    def set_wave_object(self, wave_obj):
        self.stop()

        self.playback_thread = AudioPlaybackThread(wave_obj)
        self.playback_thread.errorOccurred.connect(self.errorOccurred)
        self.playback_thread.currentTimeUpdated.connect(self.currentTimeUpdated)
        self.playback_thread.finished.connect(self.finished)

        self.framerate = wave_obj.getframerate()
        self.nframes = wave_obj.getnframes()

    def isRunning(self):
        if self.playback_thread is None:
            return False
        return self.playback_thread.isRunning() and not self.playback_thread.isPaused()

    def play(self):
        if self.playback_thread is None:
            return False

        if not self.playback_thread.isRunning():
            self.playback_thread.start()
            return True
        elif self.playback_thread.isPaused():
            self.playback_thread.resume()
            return True
        return True # Already playing

    def pause(self):
        if self.playback_thread:
            self.playback_thread.pause()
            return True
        return False

    def stop(self):
        if self.playback_thread:
            self.playback_thread.stop()
            self.playback_thread.wait()  # Wait for the thread to finish
    
    def seek(self, frame_index):
        if self.playback_thread:
            self.playback_thread.seek(frame_index)