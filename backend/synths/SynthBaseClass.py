import numpy as np
import wave
import io

class SynthBaseClass():
    """ Base class for all sound synthesizers"""
    def __init__(self):
        self.name = None
        self.sample_rate = 44100


    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def __call__(self, freq, amp, duration):
        """ This method is called when the synth is used as a function"""
        return self.generate(freq, amp, duration)

    def generate(self, freq, amp, duration):
        raise NotImplementedError("generate(self, freq, amp, duration) must be implemented in Synth subclass")