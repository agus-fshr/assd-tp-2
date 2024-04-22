import mido
import json

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

    def get_midi_metadata(self, name=""):
        if name in self.midi_objects:
            midi_obj = self.midi_objects[name]
            track_meta = {}
            
            for i, track in enumerate(midi_obj.tracks):
                # get MetaMessages from the track
                meta_msgs = [msg.dict() for msg in track if isinstance(msg, mido.MetaMessage)]
                track_meta[f"track_{i}"] = meta_msgs

            midi_meta = {
                "name": name,
                "type": midi_obj.type,
                "ticks_per_beat": midi_obj.ticks_per_beat,
                "length": midi_obj.length,
                "trackCount": len(midi_obj.tracks),
                "trackMeta": track_meta
            }
            return json.dumps(midi_meta, indent=4)
        else:
            raise ValueError(f"MIDI Object '{name}' not found in the list")