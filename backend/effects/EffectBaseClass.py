import numpy as np
import wave
import io

# DO NOT MODIFY THIS CLASS
class EffectBaseClass():
    """ Base class for all sound effects"""
    def __init__(self):
        self.name = None
        self.sample_rate = 44100

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def __call__(self, sound):
        """ This method is called when the synth is used as a function"""
        return self.process(sound)

    def process(self, sound):
        raise NotImplementedError("process() must be implemented in Synth subclass")