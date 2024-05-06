import numpy as np
from scipy import signal
from backend.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList

from .EnvelopeModulators import LinearADSR
from .SynthBaseClass import SynthBaseClass

class KSGuitar(SynthBaseClass):
    """ Simple Karplus-Strong Guitar String Synthesizer"""
    def __init__(self):
        super().__init__()

        self.name = "Karplus-Strong Guitar"

        self.params = ParameterList(
            NumParam("Stretch Factor", interval=(0, 10e3), value=0, step=0.1, text="Stretch Factor"),
            ChoiceParam("Initial Noise", options=["Normal", "Uniform", "2-Level"], value="Normal", text="Initial Noise"),
        )

    def init_wavetable(self, amp):
        """ Initialize the wavetable """
        self.L = int(np.floor(self.fs / int(self.pitch) - 1/2/stretch))
        match noise_type:
            case "Normal":
                return (amp * np.random.normal(0,1,self.L)).astype(np.float32)
            case "Uniform":
                return (amp * np.random.uniform(-1, 1, self.L)).astype(np.float32)
            case "2-Level":
                return (amp * 2 * np.random.randint(0, 2, self.L) - 1).astype(np.float32)
        

    def generate(self, freq, amp, duration):
        """ 
        Generate a Karplus-Strong guitar string sound
        - freq: tone frequency [Hz]
        - amp: tone amplitude [0, 1]
        - duration: on-off note duration [s]  
        """
        noise_type = self.params["Initial Noise"]
        stretch = self.params["Stretch Factor"]