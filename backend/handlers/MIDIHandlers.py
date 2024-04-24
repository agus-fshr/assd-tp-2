
# Y que estoy usando una lista en vez de un dict
import mido
import json

class FileImportHandler:
    def __init__(self, fileTypes="All Files (*.*)"):
        self.files_to_import = {}   # dict of file metadata indexed by keyname
        self.fileTypes = fileTypes

    def available_files(self):
        keys = []
        for key in self.files_to_import.keys():
            if self.files_to_import[key]["status"] == "OK":
                keys.append(key)
        return keys            

    # Add files to the list of files pending to import
    def add(self, filepaths=[]):
        for path in filepaths:
            filename = path.split("/")[-1]
            if filename in self.files_to_import.keys():
                raise ValueError(f"File named '{filename}' already exists in the list")
            else:
                self.files_to_import[filename] = dict(path=path, status="Pending")

    def status(self, keyname):
        return self.files_to_import[keyname]["status"]

    def path(self, keyname):
        return self.files_to_import[keyname]["path"]

    def set_status(self, keyname, status):
        self.files_to_import[keyname]["status"] = status

    def clear(self):
        self.files_to_import = {}
    
    @property
    def all_names(self):
        return self.files_to_import.keys()

    def name(self, i):
        return self.files_to_import.keys()[i]

    def rename(self, i, new_name):
        if new_name == "":
            raise ValueError("Name cannot be empty")
        # check if the proposed name already exists, if so, don't allow the change
        key_list = list(self.files_to_import.keys())
        if new_name in key_list and key_list.index(new_name) != i:
            raise ValueError(f"File named '{new_name}' already exists in the list")
        self.files_to_import[new_name] = self.files_to_import.pop(key_list[i])




class MIDIFilesHandler:
    def __init__(self):
        self.midi_objects = {}      # dict of mido.MidiFile objects indexed by path
        
    def get(self, path):
        return self.midi_objects[path]

    def delete(self, path):
        del self.midi_objects[path]

    def clear(self):
        self.midi_objects = {}

    # Import the MIDI file and store in midi_objects
    def import_midi_file(self, path) -> bool:
        try:
            self.midi_objects[path] = mido.MidiFile(path)
        except Exception as e:
            print(f"Error importing {path}: {e}")
            return False
        return True


    # Returns a dict with information about the requested MIDI file
    def get_midi_metadata(self, path):
        if path in self.midi_objects:
            midi_obj = self.midi_objects[path]
            
            track_meta = []
            for i, track in enumerate(midi_obj.tracks):
                # get MetaMessages from the track
                track_meta.append(self.metaMessageParser(track))

            midi_meta = {
                "path": path,
                "type": midi_obj.type,
                "ticks_per_beat": midi_obj.ticks_per_beat,
                "length": midi_obj.length,
                "trackCount": len(midi_obj.tracks),
                "trackMeta": track_meta
            }
            return midi_meta
        else:
            raise ValueError(f"MIDI Object from '{path}' not found in the midi_objects dict")
        
        
    # Returns a pretty json string with information about the requested MIDI file
    def get_pretty_midi_metadata_str(self, path):
        midi_meta = self.get_midi_metadata(path)
        if isinstance(midi_meta, dict):
            return json.dumps(midi_meta, indent=4)
        

    @staticmethod
    def metaMessageParser(track):
        track_data = {}
        
        ticks = 0
        refChannels = []
        for msg in track:
            ticks += msg.time

            # if "channel" is in msg, add it to refChannels
            if hasattr(msg, "channel"):
                if msg.channel not in refChannels:
                    refChannels.append(msg.channel)

            if isinstance(msg, mido.MetaMessage):
                msg = msg.dict()
                t = msg["type"]

                if t == "track_name":
                    track_data["name"] = msg["name"]
                            
                elif t == "midi_port":
                    track_data["port"] = msg["port"]

                elif t == "channel_prefix":
                    track_data["channel_prefix"] = msg["channel"]
        track_data["ticks"] = ticks
        track_data["refChannels"] = refChannels
        return track_data