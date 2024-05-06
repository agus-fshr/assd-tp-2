import mido
import json

class MidiNoteData:
    def __init__(self, note, vel, time_on=0.0, time_off=0.0):
        self.time_on = time_on
        self.time_off = time_off
        self.duration = 0.0
        self.note = note
        self.vel = vel

    def set_duration(self, time_off):
        self.time_off = time_off
        self.duration = self.time_off - self.time_on

    def time(self):
        if self.time_off >= 0.0 and self.time_on == 0.0:
            return self.time_off
        elif self.time_on >= 0.0 and self.time_off == 0.0:
            return self.time_on
        else:
            return min(self.time_on, self.time_off)


    def on_off(self):
        if self.duration != 0.0:
            raise ValueError("Note has duration, not on_off")
        
        elif self.time_off > 0.0 or self.vel == 0:
            return False
        
        elif self.time_on >= 0.0 and self.time_off == 0.0:
            return True
        
        else:
            raise ValueError("Note has no time_on or time_off")

    def __str__(self):
        if self.duration != 0.0:
            timestr = f"{self.time_on:.03f}".ljust(8)
            durstr = f"{self.duration:.03f}".ljust(5)
            return f"{timestr} + {durstr} N:{self.note} V:{self.vel}"
        
        elif self.time_off > 0.0 or self.vel == 0:
            return f"N:{self.note:03} V:{self.vel:03}\t\t t={self.time_off:.03f} OFF"
        
        elif self.time_on >= 0.0 and self.time_off == 0.0:
            return f"N:{self.note:03} V:{self.vel:03} t={self.time_on:.03f} ON"
        
        else:
            return str(self.__dict__)

class MidiMusicData:
    def __init__(self, path, title):
        self.path = path
        self.title = title
        self.channel_raw_notes = {}     # dict of notes indexed by channel
        self.chanel_notes_with_duration = {}


    def appendNote(self, channel=0, absTime=0.0, ntype="", note=0, vel=0):
        if "note_" not in ntype:
            return
        
        # if channel not in dict, add it
        if channel not in self.channel_raw_notes:
            self.channel_raw_notes[channel] = {}
            self.chanel_notes_with_duration[channel] = {}

        if note not in self.channel_raw_notes[channel]:
            self.channel_raw_notes[channel][note] = []

        on_off = True if ntype == 'note_on' else False

        if vel == 0:
            on_off = False

        #           0: time, 1: on_off, 2: vel
        note_data = MidiNoteData(note, vel)
        if on_off:
            note_data.time_on = absTime
        else:
            note_data.time_off = absTime

        self.channel_raw_notes[channel][note].append(note_data)


    def computeNoteDurations(self):
        self.chanel_notes_with_duration = {}

        for channel in self.channel_raw_notes.keys():
            note_on_dict = {}


            channel_notes = []

            for nkey in self.channel_raw_notes[channel].keys():

                for n in self.channel_raw_notes[channel][nkey]:

                    pitch = n.note
                    if n.on_off():  # note_on event

                        if pitch in note_on_dict and len(note_on_dict[pitch]) > 0:
                            note_on_dict[pitch].append(n)
                            print(f"Warning: note_on event without corresponding note_off event for note {pitch} in channel {channel} at time {n.time()}. Total notes: {len(note_on_dict[pitch])}")
                        else:
                            note_on_dict[pitch] = [n]

                    else:  # note_off event
                        if pitch in note_on_dict and note_on_dict[pitch]:
                            prevNote = note_on_dict[pitch].pop(0)
                            prevNote.set_duration(n.time_off)
                            channel_notes.append(prevNote)
                        else:
                            print(f"Warning: note_off event without corresponding note_on event for note {pitch} in channel {channel}")

            self.chanel_notes_with_duration[channel] = channel_notes

    def channels(self):
        return self.chanel_notes_with_duration.keys()

    def getChannelRawNotes(self, channel):
        return self.channel_raw_notes[channel]

    def getChannelNotes(self, channel):
        if self.chanel_notes_with_duration[channel] == {}:
            self.computeNoteDurations()
        return self.chanel_notes_with_duration[channel]
        


class MIDIFilesHandler:
    def __init__(self):
        self.midi_objects = {}      # dict of mido.MidiFile objects indexed by path
        self.midi_metadata = {}     # dict of metadata indexed by path

        self.current_midi_data = None    # current midi object

    def parseMidiNotes(self, path):
        midi = self.midi_objects[path]

        midi_data = MidiMusicData(path, self.midi_metadata[path]["trackMeta"][0]["name"])

        totTime = 0
        for msg in midi:
            if hasattr(msg, 'time'):
                totTime += msg.time

            if (msg.type == 'note_on' or msg.type == 'note_off'):
                midi_data.appendNote(msg.channel, totTime, msg.type, msg.note, msg.velocity)
        
        self.current_midi_data = midi_data
        return midi_data


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