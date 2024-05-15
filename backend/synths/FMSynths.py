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

def DFM(t, f1, f2, amplitude, I1, I2, attack_time, k):
    tau = attack_time/4
    return amplitude * np.sin( I1 * np.sin(2 * np.pi * f1 * (1-k* np.exp(-t/tau)) * t) +  I2 * np.sin(2 * np.pi * f2 *(1-k * np.exp(-t/tau)) * t) )

def DFM_1(t, f1, f2, amplitude, I1, I2):

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
            NumParam("N1", interval=(0, 10), value=1.365, step=0.001, text="Carrier multiplier"), #Ajustado por Sully y Agus
            NumParam("N2", interval=(0, 10), value=0.91, step=0.001, text="Modulator multiplier"), #Ajustado por Sully y Agus
            
            NumParam("a1", interval=(0, 1), value=0.1, step=0.01, text="Attack time, modulator "),
            NumParam("d1", interval=(0, 1), value=0.1, step=0.001, text="Decay time, modulator "),
            NumParam("s1", interval=(0, 1), value=0.99, step=0.1, text="Sustain final value, modulator "), #[0,1] as a fraction of the sustain value that will be dropped
            NumParam("r1", interval=(0, 1), value=0.05, step=0.01, text="Release time, modulator "),
            NumParam("k1", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, modulator "),
            NumParam("fmConst", interval=(-10, 10), value=0.16, step=0.01, text="Modulation frequency addition"),
            NumParam("k2d", interval=(0, 1), value=0.4, step=0.01, text="Linear rise time, modulator "),
            NumParam("n", interval=(0.1, 20), value=5, step=0.01, text="exponential deformation"),
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

        n_var = float(self.params["n"])
        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N1 = float(self.params["N1"])         #Modulation-carrier frequency relations
        N2 = float(self.params["N2"])
        fmConst = float(self.params["fmConst"]) #additional frequency value

        if duration < a2+d2+r2 :
            duration = a2+d2+r2
        
        adsr = LinearADSR(1/k2, a2, d2, r2, modType="exp", n = n_var )          # Sustain time is calculated internally
        adsr.set_total_time(duration, self.sample_rate)
        
        t = adsr.time()
        #envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        #total_time = duration + r2                    # Total time is the note duration + Release time

        fp = N1 * freq                  #frecuencia de la portadora
        fm = N2 *freq +fmConst                   #frecuencia de la modulante

        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        #t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        if I1>I2:
            modulationIndex =I1 -modIndex(t,duration) 
        else:
            modulationIndex = I1 + modIndex(t,duration) 

        fmwave = amp * FM_senoidal(t,fp, fm, 1, modulationIndex)


        return fmwave * adsr.envelope()
    
class FM_Bassoon(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "Bassoon Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("I1", interval=(-1, 10), value=0, step=0.1, text="Min mod index"),
            NumParam("I2", interval=(0, 10), value=5, step=0.1, text="Max mod index"),
            NumParam("N1", interval=(0, 10), value=5, step=0.1, text="Carrier multiplier"), #Ajustado por Sully y Agus
            NumParam("N2", interval=(0, 10), value=1, step=0.1, text="Modulator multiplier"), #Ajustado por Sully y Agus
            
            NumParam("a1", interval=(0, 1), value=0.1, step=0.01, text="Attack time, modulator "),
            NumParam("d1", interval=(0, 1), value=0.1, step=0.001, text="Decay time, modulator "),
            NumParam("s1", interval=(0, 1), value=0.99, step=0.1, text="Sustain final value, modulator "), #[0,1] as a fraction of the sustain value that will be dropped
            NumParam("r1", interval=(0, 1), value=0.05, step=0.01, text="Release time, modulator "),
            NumParam("k1", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, modulator "),
            NumParam("fmConst", interval=(-10, 10), value=0.16, step=0.01, text="Modulation frequency addition"),
            NumParam("k2d", interval=(0, 1), value=0.4, step=0.01, text="Linear rise time, modulator "),
            NumParam("n", interval=(0.1, 20), value=5, step=0.01, text="exponential deformation"),
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

        n_var = float(self.params["n"])
        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N1 = float(self.params["N1"])         #Modulation-carrier frequency relations
        N2 = float(self.params["N2"])
        fmConst = float(self.params["fmConst"]) #additional frequency value

        if duration < a2+d2+r2 :
            duration = a2+d2+r2
        
        adsr = LinearADSR(1/k2, a2, d2, r2, modType="exp", n = n_var )          # Sustain time is calculated internally
        adsr.set_total_time(duration, self.sample_rate)
        
        t = adsr.time()
        #envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        #total_time = duration + r2                    # Total time is the note duration + Release time

        fp = N1 * freq                  #frecuencia de la portadora
        fm = N2 *freq +fmConst                   #frecuencia de la modulante

        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        #t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        if I1>I2:
            modulationIndex =I1 -modIndex(t,duration) 
        else:
            modulationIndex = I1 + modIndex(t,duration) 

        fmwave = amp * FM_senoidal(t,fp, fm, 1, modulationIndex)


        return fmwave * adsr.envelope()
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

            NumParam("n", interval=(0.1, 20), value=5, step=0.01, text="exponential deformation"),
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
        
        n_var = float(self.params["n"])
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
        
        adsr = LinearADSR(1/k2, a2, d2, r2, modType="exp", n = n_var )          # Sustain time is calculated internally
        adsr.set_total_time(duration, self.sample_rate)
        
        t = adsr.time()
        #envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        
        #total_time = duration + r2                    # Total time is the note duration + Release time

        f1 = N1 * freq                  #frecuencia de la primera modulante
        f2 = N2 *freq                   #frecuencia de la segunda modulante
        
        modIndex = GenerateModIndex(I1, I2, a1, d1, r1, k1, k2d, s1) 
        #t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)

        
        fmwave = DFM_1(t,f1, f2, 1, I1, I2)


        return fmwave *amp *adsr.envelope()
    
class DFM_SAX(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Sax Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0.1, step= 0.01, text= "constante de ajuste Saxo"),
            NumParam("I11", interval=(0, 10), value=5.055, step=0.00001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=0.5, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=2.073, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=4.222, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=0.5, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=0.526, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM2"), 

            NumParam("I31", interval=(0, 10), value=0.718, step=0.1, text="Modulation index 1 DFM3"),
            NumParam("N31", interval=(0, 10), value=1, step=0.001, text="1st mod freq multiplier DFM3"), 
            NumParam("I32", interval=(0, 10), value=0.355, step=0.1, text="Modulation index 2 DFM3"),
            NumParam("N32", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM3"), 
            
            NumParam("W1", interval=(0, 10), value=0.52509, step=0.0001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=1.27713, step=0.00001, text="Weight DFM2"), 
            NumParam("W3", interval=(-1, 10), value=4.19095, step=0.00001, text="Weight DFM3"), 
            
            NumParam("n", interval=(0.1, 20), value=5, step=0.01, text="exponential deformation"),
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
        I11 = float(self.params["I11"])       
        I12 = float(self.params["I12"])

        I21 = float(self.params["I21"])       
        I22 = float(self.params["I22"]) 

        I31 = float(self.params["I31"])       
        I32 = float(self.params["I32"]) 
        
        n_var = float(self.params["n"])
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
        
        adsr = LinearADSR(1/k2, a2, d2, r2, modType="exp", n = n_var )          # Sustain time is calculated internally
        adsr.set_total_time(duration, self.sample_rate)
        
        t = adsr.time()
        #envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        #total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        
        f31 = N31 *freq                   #frecuencia de la primer modulante
        f32 = N32 *freq                   #frecuencia de la segunda modulante

        #t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)

        amp3 = W3/normaPesos
        DFM3 = DFM_1(t,f31, f32, amp3, I31, I32)

        
        fmwave = amp * (DFM1 + DFM2 + DFM3)


        return fmwave * adsr.envelope()
    
class DFM_OBOE(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Oboe Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0.05, step= 0.01, text= "constante de ajuste Oboe"),

            NumParam("I11", interval=(0, 10), value=1.618, step=0.001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=1.5, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=0.961, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=2, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=1.44, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=1.0, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=0.118, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM2"), 
            
            NumParam("W1", interval=(0, 10), value=0.776809, step=0.00001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=1.977013, step=0.00001, text="Weight DFM2"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
        I11 = float(self.params["I11"])       
        I12 = float(self.params["I12"])

        I21 = float(self.params["I21"])       
        I22 = float(self.params["I22"]) 
        

        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N11 = float(self.params["N11"])         #Modulator frequencies. (multipliers)
        N12 = float(self.params["N12"])  

        N21 = float(self.params["N21"])         #Modulator frequencies. (multipliers)
        N22 = float(self.params["N22"]) 

        W1 = float(self.params["W1"])
        W2 = float(self.params["W2"])

        normaPesos = np.sqrt(W1**2 + W2**2)

        if duration < a2+d2 :
            duration = a2+d2
        

        envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)


        
        fmwave = amp * (DFM1 + DFM2)


        return fmwave * envelope(t, duration)

class DFM_FrenchHorn(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM French Horn Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0, step= 0.01, text= "cte de French Horn"),

            NumParam("I11", interval=(0, 10), value=0.384, step=0.001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=1, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=3.174, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=5.475, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=0.5, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=3.055, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM2"), 
            
            NumParam("W1", interval=(0, 10), value=2.82625, step=0.00001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value= - 0.02898, step=0.00001, text="Weight DFM2"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
        I11 = float(self.params["I11"])       
        I12 = float(self.params["I12"])

        I21 = float(self.params["I21"])       
        I22 = float(self.params["I22"]) 
        

        a2 = float(self.params["a2"])       #Signal envelope params
        d2 = float(self.params["d2"])
        s2 = float(self.params["s2"])
        r2 = float(self.params["r2"])
        k2 = float(self.params["k2"])

        N11 = float(self.params["N11"])         #Modulator frequencies. (multipliers)
        N12 = float(self.params["N12"])  

        N21 = float(self.params["N21"])         #Modulator frequencies. (multipliers)
        N22 = float(self.params["N22"]) 

        W1 = float(self.params["W1"])
        W2 = float(self.params["W2"])

        normaPesos = np.sqrt(W1**2 + W2**2)

        if duration < a2+d2 :
            duration = a2+d2
        

        envelope = WoodwindEnvelope(amp, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)


        
        fmwave = amp * (DFM1 + DFM2)


        return fmwave * envelope(t, duration)
    
class DFM_Harpsichord(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Harpsichord Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0.1, step= 0.01, text= "constante de ajuste Harpsichord"),
            NumParam("I11", interval=(0, 10), value=2.367, step=0.00001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=0.5, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=1.607, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=4.377, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=0.5, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=0.509, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM2"), 

            NumParam("I31", interval=(0, 10), value=0.745, step=0.1, text="Modulation index 1 DFM3"),
            NumParam("N31", interval=(0, 10), value=1, step=0.001, text="1st mod freq multiplier DFM3"), 
            NumParam("I32", interval=(0, 10), value=0.189, step=0.1, text="Modulation index 2 DFM3"),
            NumParam("N32", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM3"), 
            
            NumParam("W1", interval=(0, 10), value=0.546932, step=0.000001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=1.056423, step=0.000001, text="Weight DFM2"), 
            NumParam("W3", interval=(-1, 10), value=3.433636, step=0.000001, text="Weight DFM3"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.02, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0.0001, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
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

        d2 = duration - a2
        

        adsr = LinearADSR(1/k2, a2, d2, r2, modType="linear", n = 9.4)          # Sustain time is calculated internally
        adsr.set_total_time(duration, self.sample_rate)
        
        t = adsr.time()

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        
        f31 = N31 *freq                   #frecuencia de la primer modulante
        f32 = N32 *freq                   #frecuencia de la segunda modulante

       
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)

        amp3 = W3/normaPesos
        DFM3 = DFM_1(t,f31, f32, amp3, I31, I32)

        
        fmwave = amp * (DFM1 + DFM2 + DFM3)


        return fmwave * adsr.envelope()
    
class DFM_PipeOrgan(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Pipe Organ Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0.1, step= 0.01, text= "constante de ajuste Saxo"),
            NumParam("I11", interval=(0, 10), value=4.587, step=0.00001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=1, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=2.814, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=0.145, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=0.5, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=2.896, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM2"), 

            NumParam("I31", interval=(0, 10), value=0.774, step=0.1, text="Modulation index 1 DFM3"),
            NumParam("N31", interval=(0, 10), value=1, step=0.001, text="1st mod freq multiplier DFM3"), 
            NumParam("I32", interval=(0, 10), value=2.922, step=0.1, text="Modulation index 2 DFM3"),
            NumParam("N32", interval=(0, 10), value=0.5, step=0.01, text="2nd mod freq multiplier DFM3"), 
            
            NumParam("W1", interval=(0, 10), value=1.653801, step=0.000001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=2.742604, step=0.000001, text="Weight DFM2"), 
            NumParam("W3", interval=(-1, 10), value=4.337077, step=0.00001, text="Weight DFM3"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
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
        

        envelope = WoodwindEnvelope(1, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        
        f31 = N31 *freq                   #frecuencia de la primer modulante
        f32 = N32 *freq                   #frecuencia de la segunda modulante

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)

        amp3 = W3/normaPesos
        DFM3 = DFM_1(t,f31, f32, amp3, I31, I32)

        
        fmwave = amp * (DFM1 + DFM2 + DFM3)


        return fmwave * envelope(t, duration)
    
class DFM_Trumpet(SynthBaseClass):

    def __init__(self):
        super().__init__()

        self.name = "DFM Trumpet Synthesizer"

        self.params = ParameterList(
            # Add your parameters here, using NumParam, ChoiceParam or BoolParam
            NumParam("k", interval=(0, 0.9), value = 0.1, step= 0.01, text= "constante de ajuste Saxo"),
            NumParam("I11", interval=(0, 10), value=1.39, step=0.00001, text="Modulation index 1 DFM1"),
            NumParam("N11", interval=(0, 10), value=0.5, step=0.001, text="1st mod freq multiplier DFM1"), #Ajustado por Sully y Agus
            NumParam("I12", interval=(0, 10), value=1.288, step=0.00001, text="Modulation index 2 DFM1"),
            NumParam("N12", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM1"), #Ajustado por Sully y Agus

            NumParam("I21", interval=(0, 10), value=4.835, step=0.00001, text="Modulation index 1 DFM2"),
            NumParam("N21", interval=(0, 10), value=0.5, step=0.01, text="1st mod freq multiplier DFM2"), 
            NumParam("I22", interval=(0, 10), value=3.326, step=0.001, text="Modulation index 2 DFM2"),
            NumParam("N22", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM2"), 

            NumParam("I31", interval=(0, 10), value=5.246, step=0.1, text="Modulation index 1 DFM3"),
            NumParam("N31", interval=(0, 10), value=0.5, step=0.001, text="1st mod freq multiplier DFM3"), 
            NumParam("I32", interval=(0, 10), value=0.479, step=0.1, text="Modulation index 2 DFM3"),
            NumParam("N32", interval=(0, 10), value=1, step=0.01, text="2nd mod freq multiplier DFM3"), 
            
            NumParam("W1", interval=(0, 10), value=5.262182, step=0.000001, text="Weight DFM1"), 
            NumParam("W2", interval=(0, 10), value=2.81576, step=0.000001, text="Weight DFM2"), 
            NumParam("W3", interval=(-1, 10), value=4.78754, step=0.00001, text="Weight DFM3"), 
            
            
            NumParam("a2", interval=(0, 1), value=0.1, step=0.01, text="Attack time, envelope "),
            NumParam("d2", interval=(0, 1), value=0.1, step=0.001, text="Decay time, envelope "),
            NumParam("s2", interval=(0, 10), value=1, step=0.1, text="Sustain slope, envelope "),
            NumParam("r2", interval=(0, 1), value=0.05, step=0.01, text="Release time, envelope "),
            NumParam("k2", interval=(0, 1), value=0.95, step=0.01, text="Sustain constant, envelope ")
        )

    def generate(self, freq, amp, duration):
        # Add your synthesizer code here
        k = float(self.params["k"])
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
        
        
        envelope = WoodwindEnvelope(1, 1/k2, a2, d2, r2)          # Sustain time is calculated internally
        total_time = duration + r2                    # Total time is the note duration + Release time

        f11 = N11 * freq                  #frecuencia de la primera modulante
        f12 = N12 *freq                   #frecuencia de la segunda modulante
        
        f21 = N21 * freq                  #frecuencia de la primera modulante
        f22 = N22 *freq                   #frecuencia de la segunda modulante
        
        f31 = N31 *freq                   #frecuencia de la primer modulante
        f32 = N32 *freq                   #frecuencia de la segunda modulante

        t = np.linspace(0, total_time, int(total_time * self.sample_rate), False)
        amp1 = W1/normaPesos
        DFM1 = DFM_1(t,f11, f12, amp1, I11, I12)

        amp2 = W2/normaPesos
        DFM2 = DFM_1(t,f21, f22, amp2, I21, I22)

        amp3 = W3/normaPesos
        DFM3 = DFM_1(t,f31, f32, amp3, I31, I32)

        
        fmwave = amp * (DFM1 + DFM2 + DFM3)


        return fmwave * envelope(t, duration)
    