from backend.utils.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
from .SynthBaseClass import SynthBaseClass, noteNameToMidi
from scipy import signal
import numpy as np
import wave
import os
from librosa import effects

piano_samples_path = "backend/synths/samples/piano"
saxo_tenor_samples_path = "backend/synths/samples/saxo_tenor"
saxo_soprano_samples_path = "backend/synths/samples/saxo_soprano"

class SampleSynthBaseClass(SynthBaseClass):
    def __init__(self, instrument, path):
        super().__init__()
        self.instrument = instrument
        self.name = instrument + " Samples"
        self.params = ParameterList()
        
        print("Loading available samples...")
        self.samples = self.load_samples(path)

        self.sample_rate = 44100

        # compute intermediate notes using pitch shifting
        print(f"Computing intermediate notes for {instrument}...")

        min_note = min(self.samples.keys())
        max_note = max(self.samples.keys())
        for note in range(min_note - 2, max_note + 2):
            if note not in self.samples:
                self.compute_note(note)

    def compute_note(self, note):
        if note in self.samples:
            return self.samples[note]
        else:
            closest_note = min(self.samples.keys(), key=lambda n: abs(note - n))
            shift = note - closest_note
            sample = self.samples[closest_note]
            sample = effects.pitch_shift(sample, sr=self.sample_rate, n_steps=shift, res_type="kaiser_best")
            self.samples[note] = sample
            print(f"Computed note {note} for {self.instrument}")
            return sample

    def load_samples(self, path):
        print(f"Loading samples from {path}")
        samples = {}
        for file in os.listdir(path):
            if file.endswith(".wav"):
                name = file.split(".")[0]
                if name.isdigit():
                    note = int(name)
                else:
                    note = noteNameToMidi[name]
                wave_read = wave.open(f"{path}/{file}", "rb")
                array = np.frombuffer(wave_read.readframes(wave_read.getnframes()), dtype=np.int16)
                sample_rate = wave_read.getframerate()

                # Resample to 44100 Hz
                if sample_rate != self.sample_rate:
                    array = signal.resample(array, int(len(array) * self.sample_rate / sample_rate))

                array = array.astype(np.float32) / 32768.0
                samples[note] = np.array(array)
        return samples


    def generate(self, note, amp, duration):
        if note in self.samples:
            sample = self.samples[note]
        else:
            sample = self.compute_note(note)

        sample_duration = len(sample) / self.sample_rate
        if np.abs(sample_duration - duration) < 0.05:
            pass
        elif duration < 0.002:
            sample = np.zeros(int(duration * self.sample_rate))
        else:
            sample = effects.time_stretch(sample, rate = sample_duration / duration)

        max_value = np.max(np.abs(sample))
        
        sample = sample * amp / max_value

        return sample


class PianoSampleSynth(SampleSynthBaseClass):
    def __init__(self):
        super().__init__("Piano", piano_samples_path)

class SaxoTenorSampleSynth(SampleSynthBaseClass):
    def __init__(self):
        super().__init__("Saxo Tenor", saxo_tenor_samples_path)

class SaxoSopranoSampleSynth(SampleSynthBaseClass):
    def __init__(self):
        super().__init__("Saxo Soprano", saxo_soprano_samples_path)


# class YourSynth(SynthBaseClass):
#     """ Your synthesizer here"""
#     def __init__(self):
#         super().__init__()
#         self.name = "Your Synthesizer"

#         self.params = ParameterList(
#             # Add your parameters here, using NumParam, ChoiceParam or BoolParam
#         )

#     def generate(self, freq, amp, duration):

#         # Add your synthesizer code here

#         # Return the sound array
#         return np.zeros(int(duration * self.sample_rate))
