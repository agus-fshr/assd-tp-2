import mido
import json

class MIDIFilesHandler:
    def __init__(self):
        self.midi_objects = {}      # dict of mido.MidiFile objects indexed by path
        self.midi_metadata = {}     # dict of metadata indexed by path

        self.current_midi = None    # current midi object

    def get(self, path):
        return self.midi_objects[path]

    def delete(self, path):
        del self.midi_objects[path]

    def clear(self):
        self.midi_objects = {}

    # Import the MIDI file and store in midi_objects
    def import_file(self, path) -> bool:
        try:
            midi = mido.MidiFile(path)
            self.midi_objects[path] = midi
            self.midi_metadata[path] = self.parseMidiMeta(path)
        except Exception as e:
            print(f"Error importing {path}: {e}")
            return False
        return True


    # Returns a dict with information about the requested MIDI file
    def get_midi_metadata(self, path):
        if path not in self.midi_metadata:
            self.midi_metadata[path] = self.parseMidiMeta(path)
        return self.midi_metadata[path]
        

    def parseMidiMeta(self, path):
        if path in self.midi_objects:
            midi_obj = self.midi_objects[path]

            track_meta = []
            for i, track in enumerate(midi_obj.tracks):
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