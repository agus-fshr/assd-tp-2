import numpy as np
from scipy import signal
from backend.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList

from .EnvelopeModulators import LinearADSR, ModFunction
from .SynthBaseClass import SynthBaseClass

class KSGuitar(SynthBaseClass):
    """ Simple Karplus-Strong Guitar String Synthesizer"""
    def __init__(self):
        super().__init__()

        self.name = "Karplus-Strong Guitar"

        self.params = ParameterList(
            NumParam("Stretch Factor", interval=(1.0, 5.0), value=1.03, step=0.01, text="Stretch Factor"),
            ChoiceParam("Initial Noise", options=["Normal", "Uniform", "2-Level"], value="Normal", text="Initial Noise"),
            
            NumParam("r_factor", interval=(0.0, 1.0), value=0.3, step=0.01, text="Release Factor"),

            ChoiceParam("modType", options=["cos", "sin", "log", "polyFlatTop", "poly", "exp"], value="sin", text="Env Mod function"),
            NumParam("modN", interval=(0.1, 20), value=3, step=0.1, text="Mod function N"),
            NumParam("extraTime", interval=(0.0, 2.0), value=0.1, step=0.01, text="Extra Time"),
        )

    def init_wavetable(self, amp, stretch, noise_type, freq):
        """ Initialize the wavetable """
        size = int( self.sample_rate / freq - 1/(2*stretch))
        match noise_type:
            case "Normal":
                dist = (amp * np.random.normal(0,1,size)).astype(np.float32)
            case "Uniform":
                dist = (amp * np.random.uniform(-1, 1, size)).astype(np.float32)
            case "2-Level":
                dist = (amp * 2 * np.random.randint(0, 2, size) - 1).astype(np.float32)
        
        return dist - np.mean(dist)
        
    def karplus_strong(self, wavetable, n_samples, stretch_factor):

        samples = []

        curr_sample = 0
        prev_value = 0

        while len(samples) < n_samples:

            stretch = np.random.binomial(1, 1 - 1/stretch_factor)
            if stretch == 0:
                wavetable[curr_sample] = 0.5 * (wavetable[curr_sample] + prev_value)
            
            samples.append(wavetable[curr_sample])
            prev_value = samples[-1]
            curr_sample = (curr_sample + 1) % wavetable.size

        return np.array(samples)

    def generate(self, freq, amp, duration):
        """ 
        Generate a Karplus-Strong guitar string sound
        - freq: tone frequency [Hz]
        - amp: tone amplitude [0, 1]
        - duration: on-off note duration [s]  
        """
        noise_type = self.params["Initial Noise"]
        stretch = self.params["Stretch Factor"]

        wavetable = self.init_wavetable(amp, stretch, noise_type, freq)

        duration += self.params["extraTime"]
        n_samples = int(duration * self.sample_rate)

        out = self.karplus_strong(wavetable, n_samples, stretch)

        t = duration
        r_coef = self.params["r_factor"]

        modType = self.params["modType"]
        n = self.params["modN"]
        adsr = LinearADSR(1, 0, 0, t*r_coef, modType, n)

        adsr.set_total_time(t, self.sample_rate)

        return out * adsr.envelope()