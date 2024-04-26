from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker, QWaitCondition
import pyaudio
import numpy as np
import wave
import io

class AudioPlaybackThread(QThread):
    errorOccurred = pyqtSignal(str)
    currentTimeUpdated = pyqtSignal(float)  # Emit the current play time in seconds

    def __init__(self, wave_obj):
        super().__init__()
        self.wo = wave_obj
        self.is_paused = False
        self.is_stopped = False
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()


    def run(self):
        p = pyaudio.PyAudio()
        stream = None
        total_frames_read = 0 # TIME  
        try:
            stream = p.open(format=p.get_format_from_width(self.wo.getsampwidth()),
                            channels=self.wo.getnchannels(),
                            rate=self.wo.getframerate(),
                            output=True)
            chunk_size = 1024
            data = self.wo.readframes(chunk_size)
            while data and not self.is_stopped:
                stream.write(data)
                
                # Calculate the current TIME in seconds
                total_frames_read += len(data) // self.wo.getsampwidth() // self.wo.getnchannels()
                current_time = total_frames_read / float(self.wo.getframerate())
                self.currentTimeUpdated.emit(current_time)

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

    def seek(self, time_in_seconds):
        with QMutexLocker(self.mutex):
            # Calculate the frame index based on the desired time
            frame_index = int(time_in_seconds * self.wo.getframerate())
            # Use setpos() to seek to the desired frame
            try:
                self.wo.setpos(frame_index)
                if self.is_paused:
                    # If paused, wake the thread to continue from the new position
                    self.is_paused = False
                    self.pause_condition.wakeAll()
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

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_stopped = True
            self.is_paused = False  # Ensure the thread exits if it was paused
            self.pause_condition.wakeAll()  # Wake the thread if it's waiting
        self.wo.rewind()



class AudioPlayer(QObject):
    finished = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.playback_thread = None

    def set_array(self, np_array, framerate=44100, channels=1):
        # Scale the numpy array to the range of np.int16
        np_array = np.clip(np_array, -1.0, 1.0)
        np_array = np.int16(np_array * 32767)
        
        # Convert the numpy array to bytes
        byte_data = np_array.tobytes()
        
        # Create a new wave file in memory
        wave_obj = io.BytesIO()
        with wave.open(wave_obj, 'wb') as wo:
            wo.setnchannels(channels)
            wo.setsampwidth(2)  # 2 bytes for np.int16
            wo.setframerate(framerate)
            wo.writeframes(byte_data)
        
        # Reset the buffer's file position to the beginning
        wave_obj.seek(0)
        
        # Return the wave object
        self.set_wave_obj( wave.open(wave_obj, 'rb') )

    def set_wave_obj(self, wave_obj):
        # Stop the current playback thread if it exists
        if self.playback_thread:
            self.stop()
        self.playback_thread = AudioPlaybackThread(wave_obj)
        self.playback_thread.errorOccurred.connect(self.handleError)

    def play(self):
        if self.playback_thread is None or not self.playback_thread.isRunning():
            if self.playback_thread and self.playback_thread.wo:
                self.set_wave_obj(self.playback_thread.wo)
            else:
                print("Wave object for playback thread is not set.")
                return
            self.playback_thread.start()
        elif self.playback_thread.isPaused():
            self.playback_thread.resume()

    def pause(self):
        if self.playback_thread:
            self.playback_thread.pause()

    def stop(self):
        if self.playback_thread:
            self.playback_thread.stop()
            self.playback_thread.wait()  # Wait for the thread to finish
            self.finished.emit()

    def handleError(self, error_message):
        self.errorOccurred.emit(error_message)

    

