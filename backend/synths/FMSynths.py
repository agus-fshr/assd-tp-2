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

def DFM(t, f1, f2, amplitude, I1, I2):
    return amplitude * np.sin( I1 * np.sin(2 * np.pi * f1 * t) +  I2 * np.sin(2 * np.pi * f2 * t) )

def GenerateModIndex(I1, I2, attack, decay, release, k1, k2d,s1):
    amp = abs(I1 - I2)*k1

    modIndex =  WoodwindModEnvelope(amp, 1/k1, attack, decay, release,k2d, s1) 

    return modIndex


class FMSynth(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "Clarinet Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I1", interval=(0, 10), value=4, step=0.1, text="Min mod index"),
            NumParam("I2", interval=(0, 10), value=2, step=0.1, text="Max mod index"),
            NumParam("N1", interval=(0, 10), value=1.365, step=0.1, text="Carrier multiplier"), #Ajustado por Sully y Agus
            NumParam("N2", interval=(0, 10), value=0.91, step=0.1, text="Modulator multiplier"), #Ajustado por Sully y Agus
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
            fmwave = amp * FM_senoidal(t,fp, fm, 1, 3 - sawtooth(2*np.pi *t/total_time))
        else: 
            fmwave = amp * FM_senoidal(t,fp, fm, 1, modulationIndex)


        return fmwave * envelope(t, duration)
    

class FMSynthSax(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "Sax Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I1", interval=(0, 10), value=1.2, step=0.1, text="Modulation index 1"),
            NumParam("I2", interval=(0, 10), value=2.0, step=0.1, text="Modulation index 2"),
            NumParam("N1", interval=(0, 10), value=1.0, step=0.001, text="1st mod freq multiplier"), 
            NumParam("N2", interval=(0, 10), value=2.0, step=0.01, text="2nd mod freq multiplier"), 
            
            
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

        f1 = N1 * freq                  #frecuencia de la primera modulante
        f2 = N2 *freq                   #frecuencia de la segunda modulante
        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        
        fmwave = amp * DFM(t,f1, f2, 1, I1, I2)


        return fmwave * envelope(t, duration)
    
class DFM_SAX(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Sax Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I11", interval=(0, 10), value=1.47038, step=0.00001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=1.0, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=0.032411, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=0.49422, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=1.0, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=3.222, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM2"), 

            NumParam("I31", interval=(0, 10), value=2.7882, step=0.1, text="Modulation index 1 DFM3"),
            NumParam("N31", interval=(0, 10), value=1.5, step=0.001, text="1st mod freq multiplier DFM3"), 
            NumParam("I32", interval=(0, 10), value=4.895, step=0.1, text="Modulation index 2 DFM3"),
            NumParam("N32", interval=(0, 10), value=1.0, step=0.01, text="2nd mod freq multiplier DFM3"), 
            
            NumParam("W1", interval=(0, 10), value=2.2044, step=0.0001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=1.80192, step=0.00001, text="Weight DFM2"), 
            NumParam("W3", interval=(-1, 10), value=-0.23908, step=0.00001, text="Weight DFM3"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here

        I11 = float(self.params["I11"])       
        I12 = float(self.params["I12"])

        I21 = float(self.params["I21"])       
        I22 = float(self.params["I22"]) 

        I31 = float(self.params["I31"])       
        I32 = float(self.params["I32"]) 
        

        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N11 = float(self.params["N11"])         #Modulator frequencies. (multipliers)
        N12 = float(self.params["N12"])  

        N21 = float(self.params["N21"])         #Modulator frequencies. (multipliers)
        N22 = float(self.params["N22"]) 

        N31 = float(self.params["N31"])         #Modulator frequencies. (multipliers)
        N32 = float(self.params["N32"])        
        
        W1 = float(self.params["W1"])
        W2 = float(self.params["W2"])
        W3 = float(self.params["W3"])

        normaPesos = np.sqrt(W1**2 + W2**2 + W3**2)

        if duration < a2+d2 :
            duration = a2+d2
        

        envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        
        f31 = N31 *freq                   #frecuencia de la primer modulante
        f32 = N32 *freq                   #frecuencia de la segunda modulante

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM(t,f21, f22, amp2, I21, I22)

        amp3 = W3/normaPesos
        DFM3 = DFM(t,f31, f32, amp3, I31, I32)

        
        fmwave = amp * (DFM1 + DFM2 + DFM3)


        return fmwave * envelope(t, duration)
    