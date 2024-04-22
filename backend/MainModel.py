import mido

class MainModel:
    def __init__(self):
        self.file_metadata = [] # list of dict(name, path, status)
        self.midi_objects = {}  # dict of mido.MidiFile objects indexed by <name>

    # Add files to the list of files to import
    def add_files(self, filepaths=[]):
        for path in filepaths:
            filename = path.split("/")[-1]
            # check if filename key already exists in metadata
            exists=False
            for fm in self.file_metadata:
                if fm["name"] == filename:
                    exists=True
                    break
            if exists:
                raise ValueError(f"File named '{filename}' already exists in the list")
            else:
                self.file_metadata.append(dict(name=filename, path=path, status="Pending"))

    # Import the MIDI files and store them in midi_objects
    def import_files(self):
        self.midi_objects = {}
        for file_metadata in self.file_metadata:
            path = file_metadata["path"]
            name = file_metadata["name"]
            try:
                self.midi_objects[name] = mido.MidiFile(path)
            except Exception as e:
                file_metadata["status"] = "ERROR"
                print(f"Error importing {file_metadata['name']}: {e}")
                continue
            file_metadata["status"] = "OK"