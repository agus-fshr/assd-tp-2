from backend.utils.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
from .SynthBaseClass import SynthBaseClass
from scipy import signal
import numpy as np
from .EnvelopeModulators import LinearADSR
from .EnvelopeModulators import WoodwindEnvelope
from .EnvelopeModulators import WoodwindModEnvelope
from scipy.signal import sawtooth

def FM_senoidal(t, fp, fm, amplitude, m):
    return amplitude * np.sin(2 * np.pi * fp * t - (np.pi /2) +  m * np.sin(2 * np.pi * fm * t - (np.pi /2)))

def GenerateModIndex(I1, I2, attack, decay, release, k1, k2d,s1):
    amp = abs(I1 - I2)*k1

    modIndex =  WoodwindModEnvelope(amp, 1/k1, attack, decay, release,k2d, s1) 

    return modIndex


class FMSynth(SynthBaseClass):
    """ Your synthesizer here"""
    def __init__(self):
        super().__init__()

        self.name = "FM Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I1", interval=(0, 10), value=4, step=0.1, text="Min mod index"),
            NumParam("I2", interval=(0, 10), value=2, step=0.1, text="Max mod index"),
            NumParam("N1", interval=(0, 10), value=1.365, step=0.1, text="Carrier multiplier"), #Ajustado por Sully y Agus
            NumParam("N2", interval=(0, 10), value=0.91, step=0.1, text="Modulator multiplier"), #Ajustado por Sully y Agus
            BoolParam("Testing", value= True, text="Testing Sawtooth"),
            
            NumParam("a1", interval=(0, 1), value=0.1, step=0.01, text="Attack time, modulator "),
            NumParam("d1", interval=(0, 1), value=0.1, step=0.001, text="Decay time, modulator "),
            NumParam("s1", interval=(0, 1), value=0.99, step=0.1, text="Sustain final value, modulator "), #[0,1] as a fraction of the sustain value that will be dropped
            NumParam("r1", interval=(0, 1), value=0.05, step=0.01, text="Release time, modulator "),
            NumParam("k1", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, modulator "),
            NumParam("fmConst", interval=(-10, 10), value=0.16, step=0.01, text="Modulation frequency addition"),
            NumParam("k2d", interval=(0, 1), value=0.4, step=0.01, text="Linear rise time, modulator "),

            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here

        I1 = float(self.params["I1"])       #Modulation index limits
        I2 = float(self.params["I2"])

        a1 = float(self.params["a1"])       #Modulator envelope params
        d1 = float(self.params["d1"])   
        s1 = float(self.params["s1"])
        r1 = float(self.params["r1"])
        k1 = float(self.params["k1"])
        k2d = float(self.params["k2d"])
        testMod = bool(self.params["Testing"])

        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N1 = float(self.params["N1"])         #Modulation-carrier frequency relations
        N2 = float(self.params["N2"])
        fmConst = float(self.params["fmConst"]) #additional frequency value

        if duration < a2+d2 :
            duration = a2+d2
        

        envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        fp = N1 * freq                  #frecuencia de la portadora
        fm = N2 *freq +fmConst                   #frecuencia de la modulante

        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        if I1>I2:
            modulationIndex =I1 -modIndex(t,duration) 
        else:
            modulationIndex = I1 + modIndex(t,duration) 

        if testMod:
            fm = amp * FM_senoidal(t,fp, fm, 1, 3 - sawtooth(2*np.pi *t/total_time))
        else: 
            fm = amp * FM_senoidal(t,fp, fm, 1, modulationIndex)


        return fm * envelope(t, duration)
    

class FMSynthSax(SynthBaseClass):
    """ Your synthesizer here"""
    def __init__(self):
        super().__init__()

        self.name = "FM Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I1", interval=(0, 10), value=4, step=0.1, text="Min mod index"),
            NumParam("I2", interval=(0, 10), value=2, step=0.1, text="Max mod index"),
            NumParam("N1", interval=(0, 10), value=1.365, step=0.001, text="Carrier multiplier"), #Ajustado por Sully y Agus
            NumParam("N2", interval=(0, 10), value=0.91, step=0.01, text="Modulator multiplier"), #Ajustado por Sully y Agus
            BoolParam("Testing", value= False, text="Testing Sawtooth"),
            
            NumParam("a1", interval=(0, 1), value=0.1, step=0.01, text="Attack time, modulator "),
            NumParam("d1", interval=(0, 1), value=0.1, step=0.001, text="Decay time, modulator "),
            NumParam("s1", interval=(0, 1), value=0.99, step=0.1, text="Sustain final value, modulator "), #[0,1] as a fraction of the sustain value that will be dropped
            NumParam("r1", interval=(0, 1), value=0.05, step=0.01, text="Release time, modulator "),
            NumParam("k1", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, modulator "),
            NumParam("fmConst", interval=(-10, 10), value=0.16, step=0.01, text="Modulation frequency addition"),
            NumParam("k2d", interval=(0, 1), value=0.4, step=0.01, text="Linear rise time, modulator "),

            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here

        I1 = float(self.params["I1"])       #Modulation index limits
        I2 = float(self.params["I2"])

        a1 = float(self.params["a1"])       #Modulator envelope params
        d1 = float(self.params["d1"])   
        s1 = float(self.params["s1"])
        r1 = float(self.params["r1"])
        k1 = float(self.params["k1"])
        k2d = float(self.params["k2d"])
        testMod = bool(self.params["Testing"])

        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N1 = float(self.params["N1"])         #Modulation-carrier frequency relations
        N2 = float(self.params["N2"])
        fmConst = float(self.params["fmConst"]) #additional frequency value

        if duration < a2+d2 :
            duration = a2+d2
        

        envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        fp = N1 * freq                  #frecuencia de la portadora
        fm = N2 *freq +fmConst                   #frecuencia de la modulante

        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        if I1>I2:
            modulationIndex =I1 -modIndex(t,duration) 
        else:
            modulationIndex = I1 + modIndex(t,duration) 

        if testMod:
            fm = amp * FM_senoidal(t,fp, fm, 1, 3 - sawtooth(2*np.pi *t/total_time))
        else: 
            fm = amp * FM_senoidal(t,fp, fm, 1, modulationIndex)


        return fm * envelope(t, duration)