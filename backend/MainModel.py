
from .handlers.MIDIHandler import *
from .handlers.FileHandler import *
from .handlers.WavHandler import *

from .synths.Synthesizers import *
from .effects.Effects import *

from .audio.AudioPlayer import AudioPlayer

class MainModel:
    def __init__(self):
        self.file_handler = FileImportHandler(fileTypes="All Files (*.*);;MIDI Files (*.mid);;WAV Files (*.wav)")
        self.midi_handler = MIDIFilesHandler()
        self.wav_handler = WavHandler()

        self.audioPlayer = AudioPlayer()

        # Add synthesizers here !
        self.synthesizers = [
            PureToneSynth(),
        ]

        # Add effects here !
        self.effects = [
            NoEffect(),
            DelayEffect(),
            # ReverbEffect(),
        ]


    def import_files(self):
        self.import_wav_files()
        self.import_midi_files()


    def import_wav_files(self):
        for fmeta in self.file_handler.pending_files("wav"):
            if self.wav_handler.import_wav_file(fmeta.path):
                fmeta.set_ok()
            else:
                fmeta.set_error()

    def import_midi_files(self):
        for fmeta in self.file_handler.pending_files("mid"):
            if self.midi_handler.import_midi_file(fmeta.path):
                fmeta.set_ok()
            else:
                fmeta.set_error()
