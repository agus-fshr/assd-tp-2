
from backend.handlers.MIDIHandlers import *

class MainModel:
    def __init__(self):
        self.file_handler = FileImportHandler(fileTypes="MIDI Files (*.mid)") #    ";;All Files (*.*)" 
        self.midi_handler = MIDIFilesHandler()

    def import_midi_files(self):
        for key in self.file_handler.all_names:
            path = self.file_handler.path(key)
            status = self.file_handler.status
            if status == "OK":
                continue
            
            if self.midi_handler.import_midi_file(path):
                self.file_handler.set_status(key, "OK")
            else:
                self.file_handler.set_status(key, "Error")