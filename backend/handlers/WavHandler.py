import wave
import numpy as np

class WavMetadata:
    def __init__(self, **kwargs):
        if isinstance(kwargs, dict):
            self.parse(**kwargs)
        else:
            raise ValueError("WavMetadata must be initialized with a dictionary of metadata")
        
    def from_numpy_array(self, np_array, framerate=44100):
        self.channels = np_array.shape[0]
        self.sample_width = np_array.dtype.itemsize
        self.framerate = framerate
        self.nframes = np_array.shape[1]
        self.compname = "not compressed"
        self.comptype = "NONE"
        self.seconds = np_array.shape[1] / framerate

    def parse(self, channels, sample_width, framerate, nframes, compname, comptype, seconds):
        self.channels = channels
        self.sample_width = sample_width    
        self.framerate = framerate          # Frames per second
        self.nframes = nframes              # Number of frames
        self.compname = compname
        self.comptype = comptype
        self.seconds = seconds

    def __str__(self):
        return f"({self.channels} channels, {self.sample_width} bytes/sample, {self.framerate} Hz, {self.seconds:.2f} seconds)"

    def __repr__(self):
        return f"WavMetadata({self.channels}, {self.sample_width}, {self.framerate}, {self.nframes}, {self.compname}, {self.comptype}, {self.seconds})"
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class WavHandler:
    def __init__(self):
        self.metadata = {}  # dict of metadata indexed by path

        self.data = {}      # dict of numpy arrays indexed by path


    def clear(self):
        self.metadata = {}

    def __getitem__(self, path):
        if path in self.metadata:
            return self.metadata[path]
        else:
            raise AttributeError(f"WavMetadata with path '{path}' not found in WavHandler") 

    def import_file(self, path):
        """Attempt to import a WAV file, validating it implicitly by trying to read its metadata."""
        try:
            wavMeta = self.read_wav_metadata(path)
            if wavMeta:
                self.metadata[path] = wavMeta
                return True     # Successfully imported
            else:
                return False    # Failed to import
        except wave.Error:
            return False    # Failed to import

    def read_wav_metadata(self, path):
        """Read and return WavMetadata from a WAV file."""
        try:
            with wave.open(path, 'rb') as wav_file:
                metadata = {
                    "channels": wav_file.getnchannels(),
                    "sample_width": wav_file.getsampwidth(),
                    "framerate": wav_file.getframerate(),
                    "nframes": wav_file.getnframes(),
                    "compname": wav_file.getcompname(),
                    "comptype": wav_file.getcomptype(),
                    "seconds": wav_file.getnframes() / wav_file.getframerate(),
                }
                return WavMetadata(**metadata)
        except wave.Error:
            return None