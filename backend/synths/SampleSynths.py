from backend.utils.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
from .SynthBaseClass import SynthBaseClass
from scipy import signal
import numpy as np
from .SampleSynthUtils import shift_pitch, extend, smooth
from scipy.io import wavfile

# Add the sample files here lmao
# violin_sample_rate, violin_data = wavfile.read('')
# flute_sample_rate, flute_data = wavfile.read('')
# trumpet_sample_rate, trumpet_data = wavfile.read('')
# piano_sample_rate, piano_data = wavfile.read('')


class SampleSynth(SynthBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Sample Synthesizer"

        self.params = ParameterList(
            ChoiceParam(name="Instrument", options=["Piano", "Violin", "Trumpet", "Flute"], text="Piano"),
        )

        self.instrument = self.params["Instrument"]

        match self.instrument:
            case 'violin':
                self.sample_rate = violin_sample_rate
                self.data = violin_data
                self.fundamental_frequency = 261

            case 'flute':
                self.sample_rate = flute_sample_rate
                self.data = flute_data
                self.fundamental_frequency = 392

            case 'piano':
                self.sample_rate = piano_sample_rate
                self.data = piano_data
                self.fundamental_frequency = 261

            case 'trumpet':
                self.sample_rate = trumpet_sample_rate
                self.data = trumpet_data
                self.fundamental_frequency = 261

    def generate(self, note, amp, duration):
        
        f_ratio = note / self.fundamental_frequency
        new_signal = shift_pitch(self.data, self.sample_rate, f_ratio)
        time = np.arange(0, len(new_signal) / self.sample_rate, 1 / self.sample_rate)
        out = extend(new_signal, time, duration, self.sample_rate, self.instrument)

        return out * 0.1










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
