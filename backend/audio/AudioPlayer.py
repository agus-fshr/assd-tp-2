from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker, QWaitCondition
import pyaudio


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

    def set_wave_obj(self, wave_obj):
        # Stop the current playback thread if it exists
        if self.playback_thread:
            self.stop_audio()
        self.playback_thread = AudioPlaybackThread(wave_obj)
        self.playback_thread.errorOccurred.connect(self.handleError)

    def play_audio(self):
        if not self.playback_thread or not self.playback_thread.isRunning():
            if self.playback_thread and not self.playback_thread.isRunning():
                # If the thread has finished running, reinitialize it for replay
                self.set_wave_obj(self.playback_thread.wo)
            self.playback_thread.start()
        elif self.playback_thread.isPaused():
            self.playback_thread.resume()

    def pause_audio(self):
        if self.playback_thread:
            self.playback_thread.pause()

    def stop_audio(self):
        if self.playback_thread:
            self.playback_thread.stop()
            self.playback_thread.wait()  # Wait for the thread to finish
            self.finished.emit()

    def handleError(self, error_message):
        self.errorOccurred.emit(error_message)

    

