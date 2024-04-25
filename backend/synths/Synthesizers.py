from backend.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
import numpy as np
from scipy import signal

from .EnvelopeModulators import LinearADSR
from .SynthBaseClass import SynthBaseClass

class PureToneSynth(SynthBaseClass):
    """ Simple pure tone synthesizer"""
    def __init__(self):
        super().__init__()
        self.name = "Pure Tone Synthesizer" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            ChoiceParam("waveform", options=["Sine", "Square", "Sawtooth", "Triangle"], value="Sine", text="Waveform"),
            NumParam("k", interval=(1, 4), value=4, step=0.01, text="k value"),
            NumParam("A", interval=(0, 1), value=0.0, step=0.01, text="Attack [s]"),
            NumParam("D", interval=(0, 1), value=0.15, step=0.01, text="Decay [s]"),
            NumParam("R", interval=(0, 10), value=0.45, step=0.01, text="Release [s]"),
        )

    def generate(self, freq, amp, duration):
        """ 
        Generate a pure tone with the given frequency, amplitude and duration
        - freq: tone frequency [Hz]
        - amp: tone amplitude [0, 1]
        - duration: on-off note duration [s]  
        """
        wtype = self.params["waveform"]
        wave = None
        if wtype == "Sine":
            wave = lambda x: np.sin(x)
        elif wtype == "Square":
            wave = lambda x: signal.square(x)
        elif wtype == "Sawtooth":
            wave = lambda x: signal.sawtooth(x)
        elif wtype == "Triangle":
            wave = lambda x: signal.sawtooth(x, 0.5)

        k = self.params["k"]
        A = self.params["A"]
        D = self.params["D"]
        R = self.params["R"]

        if duration < A + D:
            duration = A + D

        envelope = LinearADSR(amp, k, A, D, R)          # Sustain time is calculated internally
        total_time = duration + R                       # Total time is the note duration + Release time

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        wave = amp * wave(2 * np.pi * freq * t)

        return wave * envelope(t, duration)
    
    

# class YourSynth(SynthBaseClass):
#     """ Your synthesizer here"""