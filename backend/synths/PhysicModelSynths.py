from backend.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
from .SynthBaseClass import SynthBaseClass
from scipy import signal
import numpy as np



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