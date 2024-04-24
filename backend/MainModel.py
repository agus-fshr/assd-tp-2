
from backend.handlers.MIDIHandler import *
from backend.handlers.FileHandler import *
from backend.handlers.WavHandler import *

class MainModel:
    def __init__(self):
        self.file_handler = FileImportHandler(fileTypes="All Files (*.*);;MIDI Files (*.mid);;WAV Files (*.wav)")
        self.midi_handler = MIDIFilesHandler()
        self.wav_handler = WavHandler()

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
