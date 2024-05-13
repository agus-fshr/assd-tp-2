import numpy as np
import wave
import io
import inspect

# noteNameToMidi = {
#     "G9": 127,"F#9": 127,"Gb9": 126,"F9": 125,"E9": 124,"D#9": 124,"Eb9": 123,"D9": 122,"C#9": 122,"Db9": 121,"C9": 120,"B8": 119,"A#8": 119,"Bb8": 118,"A8": 117,"G#8": 117,"Ab8": 116,"G8": 115,"F#8": 115,"Gb8": 114,"F8": 113,"E8": 112,"D#8": 112,"Eb8": 111,"D8": 110,"C#8": 110,"Db8": 109,"C8": 108,"B7": 107,"A#7": 107,"Bb7": 106,"A7": 105,"G#7": 105,"Ab7": 104,"G7": 103,"F#7": 103,"Gb7": 102,"F7": 101,"E7": 100,"D#7": 100,"Eb7": 99,"D7": 98,"C#7": 98,"Db7": 97,"C7": 96,"B6": 95,"A#6": 95,"Bb6": 94,"A6": 93,"G#6": 93,"Ab6": 92,"G6": 91,"F#6": 91,"Gb6": 90,"F6": 89,"E6": 88,"D#6": 88,"Eb6": 87,"D6": 86,"C#6": 86,"Db6": 85,"C6": 84,"B5": 83,"A#5": 83,"Bb5": 82,"A5": 81,"G#5": 81,"Ab5": 80,"G5": 79,"F#5": 79,"Gb5": 78,"F5": 77,"E5": 76,"D#5": 76,"Eb5": 75,"D5": 74,"C#5": 74,"Db5": 73,"C5": 72,"B4": 71,"A#4": 71,"Bb4": 70,"A4": 69,"G#4": 69,"Ab4": 68,"G4": 67,"F#4": 67,"Gb4": 66,"F4": 65,"E4": 64,"D#4": 64,"Eb4": 63,"D4": 62,"C#4": 62,"Db4": 61,"C4": 60,"B3": 59,"A#3": 59,"Bb3": 58,"A3": 57,"G#3": 57,"Ab3": 56,"G3": 55,"F#3": 55,"Gb3": 54,"F3": 53,"E3": 52,"D#3": 52,"Eb3": 51,"D3": 50,"C#3": 50,"Db3": 49,"C3": 48,"B2": 47,"A#2": 47,"Bb2": 46,"A2": 45,"G#2": 45,"Ab2": 44,"G2": 43,"F#2": 43,"Gb2": 42,"F2": 41,"E2": 40,"D#2": 40,"Eb2": 39,"D2": 38,"C#2": 38,"Db2": 37,"C2": 36,"B1": 35,"A#1": 35,"Bb1": 34,"A1": 33,"G#1": 33,"Ab1": 32,"G1": 31,"F#1": 31,"Gb1": 30,"F1": 29,"E1": 28,"D#1": 28,"Eb1": 27,"D1": 26,"C#1": 26,"Db1": 25,"C1": 24,"B0": 23,"A#0": 23,"Bb0": 22,"A0": 21,"G#": 20,"G": 19,"F#": 18,"F": 17,"E": 16,"D#": 15,"D": 14,"C#": 13,"C0": 12,"B": 11,"A#": 10,"A": 9,"G#": 8,"G": 7,"F#": 6,"F": 5,"E": 4,"D#": 3,"D": 2,"C#": 1,"C1": 0,
# }

noteNameToMidi = {
    "C0": 12, "C#0": 13, "Db0": 13, "D0": 14, "D#0": 15, "Eb0": 15, "E0": 16, "F0": 17, "F#0": 18, "Gb0": 18, "G0": 19, "G#0": 20, "Ab0": 20, "A0": 21, "A#0": 22, "Bb0": 22, "B0": 23,
    "C1": 24, "C#1": 25, "Db1": 25, "D1": 26, "D#1": 27, "Eb1": 27, "E1": 28, "F1": 29, "F#1": 30, "Gb1": 30, "G1": 31, "G#1": 32, "Ab1": 32, "A1": 33, "A#1": 34, "Bb1": 34, "B1": 35,
    "C2": 36, "C#2": 37, "Db2": 37, "D2": 38, "D#2": 39, "Eb2": 39, "E2": 40, "F2": 41, "F#2": 42, "Gb2": 42, "G2": 43, "G#2": 44, "Ab2": 44, "A2": 45, "A#2": 46, "Bb2": 46, "B2": 47,
    "C3": 48, "C#3": 49, "Db3": 49, "D3": 50, "D#3": 51, "Eb3": 51, "E3": 52, "F3": 53, "F#3": 54, "Gb3": 54, "G3": 55, "G#3": 56, "Ab3": 56, "A3": 57, "A#3": 58, "Bb3": 58, "B3": 59,
    "C4": 60, "C#4": 61, "Db4": 61, "D4": 62, "D#4": 63, "Eb4": 63, "E4": 64, "F4": 65, "F#4": 66, "Gb4": 66, "G4": 67, "G#4": 68, "Ab4": 68, "A4": 69, "A#4": 70, "Bb4": 70, "B4": 71,
    "C5": 72, "C#5": 73, "Db5": 73, "D5": 74, "D#5": 75, "Eb5": 75, "E5": 76, "F5": 77, "F#5": 78, "Gb5": 78, "G5": 79, "G#5": 80, "Ab5": 80, "A5": 81, "A#5": 82, "Bb5": 82, "B5": 83,
    "C6": 84, "C#6": 85, "Db6": 85, "D6": 86, "D#6": 87, "Eb6": 87, "E6": 88, "F6": 89, "F#6": 90, "Gb6": 90, "G6": 91, "G#6": 92, "Ab6": 92, "A6": 93, "A#6": 94, "Bb6": 94, "B6": 95,
    "C7": 96, "C#7": 97, "Db7": 97, "D7": 98, "D#7": 99, "Eb7": 99, "E7": 100, "F7": 101, "F#7": 102, "Gb7": 102, "G7": 103, "G#7": 104, "Ab7": 104, "A7": 105, "A#7": 106, "Bb7": 106, "B7": 107,
    "C8": 108, "C#8": 109, "Db8": 109, "D8": 110, "D#8": 111, "Eb8": 111, "E8": 112, "F8": 113, "F#8": 114, "Gb8": 114, "G8": 115, "G#8": 116, "Ab8": 116, "A8": 117, "A#8": 118, "Bb8": 118, "B8": 119,
    "C9": 120, "C#9": 121, "Db9": 121, "D9": 122, "D#9": 123, "Eb9": 123, "E9": 124, "F9": 125, "F#9": 126, "Gb9": 126, "G9": 127
}

# DO NOT MODIFY THIS CLASS
class SynthBaseClass():
    """ Base class for all sound synthesizers"""
    def __init__(self):
        self.name = None
        self.sample_rate = 44100


    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate


    def __call__(self, note, amp, duration):
        """ This method is called when the synth is used as a function"""

        # debug_str = ""
        if isinstance(note, str):
            # debug_str = f"note: {note} "
            note = noteNameToMidi[note]
        note = int(note)
        freq = 440 * 2**((note - 69) / 12)

        # debug_str += f"{note} {freq:.2f} Hz"
        # print(debug_str)

        arg_names = inspect.getargspec(self.generate).args

        # check if generate method has "note" argument
        if "note" in arg_names:
            return self.generate(note, amp, duration)
        elif "freq" in arg_names:
            return self.generate(freq, amp, duration)
        else:
            raise Exception("generate method must have 'note' or 'freq' as an argument")

    def generate(self, note, amp, duration):
        raise NotImplementedError("generate(self, *args) must be implemented in Synth subclass")
    
