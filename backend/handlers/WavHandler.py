import wave

class WavMetadata:
    def __init__(self, path, channels, sample_width, framerate, nframes, compname, comptype, seconds):
        self.path = path
        self.channels = channels
        self.sample_width = sample_width    
        self.framerate = framerate          # Frames per second
        self.nframes = nframes              # Number of frames
        self.compname = compname
        self.comptype = comptype
        self.seconds = seconds

    def __str__(self):
        return f"{self.path} ({self.channels} channels, {self.sample_width} bytes/sample, {self.framerate} Hz, {self.seconds:.2f} seconds)"

    def __repr__(self):
        return f"WavMetadata({self.path}, {self.channels}, {self.sample_width}, {self.framerate}, {self.nframes}, {self.compname}, {self.comptype}, {self.seconds})"
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class WavHandler:
    def __init__(self):
        self.metadata = {}  # dict of metadata indexed by path

    def clear(self):
        self.metadata = {}

    def get_meta(self, path):
        return self.metadata.get(path, None)

    def get_wave(self, path):
        return wave.open(path, 'rb')

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
                return WavMetadata(path, **metadata)
        except wave.Error:
            return None