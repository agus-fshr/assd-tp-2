import mido
import json
import copy

class MidiNoteData:
    def __init__(self, note, velocity, time_on=0.0, time_off=0.0):
        self.time_on = time_on
        self.time_off = time_off
        self.duration = 0.0
        self.note = note
        self.velocity = velocity

    def set_duration(self, time_off):
        self.time_off = time_off
        self.duration = time_off - self.time_on

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
        
        elif self.time_off > 0.0 or self.velocity == 0:
            return False
        
        elif self.time_on >= 0.0 and self.time_off == 0.0 and self.velocity > 0:
            return True
        
        else:
            raise ValueError("Note has no time_on or time_off. Bad format")

    def __str__(self):
        if self.duration != 0.0:
            timestr = f"{self.time_on:.03f}".ljust(9)
            durstr = f"{self.duration:.03f}".ljust(7)
            return f"{timestr} + {durstr} N:{self.note} V:{self.velocity}"
        
        elif self.time_off > 0.0 or self.velocity == 0:
            if self.time_off > 0.0 and self.time_on > 0.0:
                self.duration = self.time_off - self.time_on
                return f"N:{self.note:03} V:{self.velocity:03}\t\t t={self.time_on:.03f} ON\t\t t={self.time_off:.03f} OFF"
            return f"N:{self.note:03} V:{self.velocity:03}\t\t t={self.time_off:.03f} OFF"
        
        elif self.time_on >= 0.0 and self.time_off == 0.0 and self.velocity > 0:
            return f"N:{self.note:03} V:{self.velocity:03} t={self.time_on:.03f} ON"
        
        else:
            return str(self.__dict__) + " ERROR"






class MidiMusicData:
    def __init__(self, path, title, handleOverlap="ignore"):
        handleOverlap_options = ["ignore", "FIFO"]
        if handleOverlap not in handleOverlap_options:
            raise ValueError(f"handleOverlap must be one of {handleOverlap_options}")

        self.handleOverlap = handleOverlap
        self.path = path
        self.title = title
        self.channel_data = {}
        self.channel_raw_notes = {}     # dict of notes indexed by channel
        self.total_duration = 0.0


    def appendNote(self, channel=0, absTime=0.0, ntype="", note=0, velocity=0):
        if "note_" not in ntype:
            return
        
        # if channel not in dict, add it
        if channel not in self.channel_raw_notes:
            self.channel_raw_notes[channel] = []

        if channel not in self.channel_data:
            self.channel_data[channel] = {
                "title": f"channel_{channel:03}",
                "notes": [],
                "duration": 0.0,
            }

        on_off = True if ntype == 'note_on' else False

        if velocity == 0:
            on_off = False

        #           0: time, 1: on_off, 2: velocity
        note_data = MidiNoteData(note, velocity)
        if on_off:
            note_data.time_on = absTime
        else:
            note_data.time_off = absTime

        self.channel_raw_notes[channel].append(note_data)


    def computeNoteDurations(self):
        for channel in self.channel_raw_notes.keys():

            note_on_dict = {}

            channel_notes = []

            for n in self.channel_raw_notes[channel]:

                pitch = n.note
                if n.on_off():  # note_on event

                    if pitch in note_on_dict and len(note_on_dict[pitch]) > 0:
                        if self.handleOverlap == "ignore":
                            continue
                        elif self.handleOverlap == "FIFO":
                            note_on_dict[pitch].append(n)

                        print(f"Warning: ON without OFF for n={pitch} in ch={channel} at t={n.time():.03f}. Tot notes={len(note_on_dict[pitch])}")
                    else:
                        note_on_dict[pitch] = [n]

                else:  # note_off
                    if pitch in note_on_dict and len(note_on_dict[pitch]) > 0:
                        if self.handleOverlap == "ignore" or self.handleOverlap == "FIFO":
                            prevNote = note_on_dict[pitch].pop(0)

                        prevNote.set_duration(n.time_off)
                        if prevNote.duration > 0:
                            channel_notes.append(prevNote)
                        elif self.handleOverlap != "ignore":
                            print(f"Warning: Note with duration=0 for n={pitch} in ch={channel} at t={n.time():.03f}")
                    else:
                        if self.handleOverlap == "ignore":
                            continue
                        print(f"Warning: OFF without ON for n={pitch} in ch={channel} at t={n.time():.03f}")

            self.channel_data[channel]["notes"] = channel_notes
            self.channel_data[channel]["duration"] = channel_notes[-1].time_off
            self.total_duration = max(self.total_duration, channel_notes[-1].time_off)

    def channels(self):
        return self.channel_raw_notes.keys()
    
    def setChannelTitle(self, channel, title):
        if channel not in self.channel_data:
            raise ValueError(f"Channel {channel} not found")
        self.channel_data[channel]["title"] = title

    def getChannelRawNotes(self, channel):
        if channel not in self.channel_raw_notes:
            raise ValueError(f"Channel {channel} not found")
        return self.channel_raw_notes[channel]

    def getChannelData(self, channel):
        if channel not in self.channel_data or len(self.channel_data[channel]["notes"]) == 0:
            self.computeNoteDurations()
        return self.channel_data[channel]

    def getChannelNotes(self, channel):
        if channel not in self.channel_raw_notes:
            raise ValueError(f"Channel {channel} not found")
        if channel not in self.channel_data or len(self.channel_data[channel]["notes"]) == 0:
            self.computeNoteDurations()
        return self.channel_data[channel]["notes"]
        
















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

        midi_data.computeNoteDurations()

        channelCount = 0
        for channel in midi_data.channels():
            names = self.get_channel_names(path, channel)
            if len(names) == 0:
                continue
            if len(names) == 1:
                pass
            else:
                print(f"Warning: Channel {channel} has more than one name: {names}")
            name = f"#{channelCount}  {names[0]}"
            midi_data.setChannelTitle(channel, name)
            channelCount += 1
        
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



    def get_channel_names(self, path, channel):
        if path not in self.midi_metadata:
            self.get_midi_metadata(path)

        names = []
        for track in self.midi_metadata[path]["trackMeta"]:
            if track["playedNotes"] > 0:
                notesRefChannels = track["notesRefChannels"]
                prefix = int(track['channel']) if "channel" in track else -999
                name = track["name"] if "name" in track else f"Unnamed Track {prefix:02}"

                if ("channel" in track) and (prefix == channel) and (channel in notesRefChannels):
                    names.append(name)
                if ("channel" not in track) and (channel in notesRefChannels):
                    names.append(name)
        return names




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
        notesRefChannels = []
        playedNotes = 0
        for msg in track:
            ticks += msg.time

            # if "channel" is in msg, add it to refChannels
            if hasattr(msg, "channel"):
                if msg.channel not in refChannels:
                    refChannels.append(msg.channel)

            msg = msg.dict()

            t = msg["type"]
            match t:
                case "track_name":
                    track_data["name"] = msg["name"]
                
                case "midi_port":
                    track_data["port"] = msg["port"]

                case "channel_prefix":
                    track_data["channel"] = msg["channel"]

                case "note_on":
                    if msg["channel"] not in notesRefChannels:
                        notesRefChannels.append(msg["channel"])
                    if msg["velocity"] > 0:
                        playedNotes += 1

                case "note_off":
                    if msg["channel"] not in notesRefChannels:
                        notesRefChannels.append(msg["channel"])

        if "name" not in track_data:
            track_data["name"] = "Unnamed Track"
            
        track_data["playedNotes"] = playedNotes
        track_data["notesRefChannels"] = notesRefChannels
        track_data["ticks"] = ticks
        track_data["refChannels"] = refChannels
        return track_data