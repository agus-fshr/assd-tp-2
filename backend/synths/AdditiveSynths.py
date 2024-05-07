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
            NumParam("k", interval=(1, 10), value=2, step=0.1, text="k value"),
            NumParam("A", interval=(0, 0.5), value=0.03, step=0.0001, text="Attack [s]"),
            NumParam("D", interval=(0, 0.5), value=0.1, step=0.0001, text="Decay [s]"),
            NumParam("R", interval=(0, 5), value=0.6, step=0.1, text="Release [s]"),
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
        

        adsr = LinearADSR(k, A, D, R, duration)     # Sustain time is calculated internally
        t = adsr.time()

        out = amp * wave(2 * np.pi * freq * t)

        return out * adsr.envelope()
    

class GuitarAdditive(SynthBaseClass):
    """ Simple pure tone synthesizer"""
    def __init__(self):
        super().__init__()

        self.name = "Guitar Additive" # Este nombre es el que se muestra en la interfaz


        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            NumParam("k", interval=(1, 10), value=2, step=0.1, text="k value"),
        )


    def generate(self, freq, amp, duration):
        """ 
        Generate a pure tone with the given frequency, amplitude and duration
        - freq: tone frequency [Hz]
        - amp: tone amplitude [0, 1]
        - duration: on-off note duration [s]  
        """        
        partials = [   # [freq, amp]
            (130.66, 0.1811),
            (261.09, 0.1278),
            (783.73, 0.0695),
            (391.75, 0.0648),
            (914.39, 0.0272),
            (1045.27, 0.0211),
            (522.41, 0.0180),
        ]

        k = self.params["k"]

        adsr = LinearADSR(k, 0.01, 0.05, 2.0, duration)     # Sustain time is calculated internally
        t = adsr.time()

        out = np.zeros(len(t))

        for f, a in partials:
            out += a * np.sin(2 * np.pi * f * t)

        return amp * out * adsr.envelope()





class YourSynth(SynthBaseClass):
    """ Your synthesizer here"""
    def __init__(self):
        super().__init__()

        self.name = "Your Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("x", interval=(0, 100), value=50, step=1, text="X value"),
            BoolParam("y", value=True, text="Y option"),
            ChoiceParam("z", options=["A", "B", "C"], value="A", text="Z option"),
        )

    def generate(self, freq, amp, duration):
        print()
        # Add your synthesizer code here

        x = float(self.params["x"])
        y = self.params["y"]
        z = self.params["z"]

        print(f"Your synth. x = {x}, type: {type(x)}")
        print(f"Your synth. y = {y}, type: {type(y)}")
        print(f"Your synth. z = {z}, type: {type(z)}")

        # Return the sound array
        print()
        return np.zeros(int(duration * self.sample_rate))



