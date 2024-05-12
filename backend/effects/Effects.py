from backend.utils.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
import numpy as np
import scipy.signal as signal

from .EffectBaseClass import EffectBaseClass

from .RIR_data import *

class NoEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "No Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList()   # Sin parametros para este efecto, pero se debe instanciar ParameterList

    def process(self, sound):
        """ Apply no effect to the sound"""
        return sound


class DelayEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Delay Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("delay", interval=(0, 1), value=0.012, step=0.001, text="Delay time [s]"),
            NumParam("feedback", interval=(0, 1), value=0.99, step=0.01, text="Feedback [0, 1]"),
        )

    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = self.params["delay"]
        feedback = self.params["feedback"]
        active = self.params["active"]
        if not active:
            return sound

        # Add zeros at the end of the sound array to allow for the delay effect
        sound = np.append(sound, np.zeros(int(5 * delay_time * self.sample_rate * (1/(1 - feedback*0.999)))))

        delay_samples = int(delay_time * self.sample_rate)
        delayed_sound = np.zeros(len(sound) + delay_samples)

        # Apply delay effect
        for i in range(len(sound)):
            delayed_sound[i + delay_samples] += sound[i] + feedback * delayed_sound[i]

        return delayed_sound
    
class SimpleEchoEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Simple Echo Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("Duration", interval=(0, 8), value=1, step=0.1, text="Durantion [repetitions]"),
            NumParam("atenuation", interval=(0, 0.99), value=0.5, step=0.01, text="Atenuation"),
        )
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = float(len(sound)/self.sample_rate)
        atenuation = float(self.params["atenuation"])
        duratio = float(self.params["Duration"])
        active = self.params["active"]
        if not active:
            return sound
        
        delay_samples = int(delay_time * self.sample_rate) +1 
        
        #amplio el array
        new_sound = np.append(np.zeros(delay_samples), sound)
        new_sound = np.append(new_sound, np.zeros(int(duratio*delay_samples)))
        
        
        sound_out = np.zeros(len(new_sound)+delay_samples)
        
        
        for i in range(delay_samples, len(sound_out)):
            sound_out[i] = new_sound[i-delay_samples] + sound_out[i - delay_samples]*atenuation
        echo_effect = sound_out[(2*delay_samples):]
        
        
        return echo_effect
    
class ReverbEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Reverb Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("delay", interval=(0, 1.2), value=0.5, step=0.01, text="Delay time [s]"),
            NumParam("Duration", interval=(0, 8), value=1, step=0.1, text="Durantion [repetitions]"),
            NumParam("atenuation", interval=(0, 0.99), value=0.5, step=0.01, text="Atenuation"),
        )
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = float(self.params["delay"])
        atenuation = float(self.params["atenuation"])
        duratio = float(self.params["Duration"])
        active = self.params["active"]
        if not active:
            return sound
        
        delay_samples = int(delay_time * self.sample_rate) +1 
        
        #amplio el array
        new_sound = np.append(np.zeros(delay_samples), sound)
        new_sound = np.append(new_sound, np.zeros(int(duratio*delay_samples)))
        
        
        sound_out = np.zeros(len(new_sound)+delay_samples)
        
        
        for i in range(delay_samples, len(sound_out)):
            sound_out[i] = new_sound[i-delay_samples] + sound_out[i - delay_samples]*atenuation
        reverb_effect = sound_out[(2*delay_samples):]
        
        
        return reverb_effect

class FlangerEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Flanger Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active")
        )
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        active = self.params["active"]
        if not active:
            return sound
        length = len(sound)
        nsamples = np.array(range(length))
        
        lfo_freq = 1/2
        lfo_amp = 0.008
        lfo = 2 + signal.sawtooth(2 * np.pi * lfo_freq * nsamples / self.sample_rate,0.5)
        index = np.around(nsamples - self.sample_rate * lfo_amp * lfo)
        index[index<0] = 0 
        index[index>(length-1)] = length - 1
        
        flanger_effect = np.zeros(length)
        for j in range(length):
            flanger_effect[j] = sound[j] + sound[int(index[j])]
        return flanger_effect
    


class ReberbRIR(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "RIR Reberb" # Este nombre es el que se muestra en la interfaz
        self.pre_loaded_rir = RIR_2
        self.rir_len = len(self.pre_loaded_rir)

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=True, text="Active"),
            ChoiceParam("lib", options=["scipy", "numpy"], value="scipy", text="Library"),
            ChoiceParam("mode", options=["full", "same", "valid"], value="full", text="Mode"),
            ChoiceParam("method", options=["auto", "direct", "fft"], value="fft", text="Method"),
            NumParam("gain", interval=(0, 1), value=0.5, step=0.01, text="RIR gain"),
            NumParam("t0", interval=(0, 5), value=0.0, step=0.001, text="Cut RIR init [s]"),
            NumParam("t1", interval=(0, 5), value=0.0, step=0.001, text="Cut RIR end [s]"),
        )   
        

    def process(self, sound):
        """ Apply no effect to the sound"""

        if not self.params["active"]:
            return sound
        
        k = self.params["gain"]
        t0 = self.params["t0"]
        t1 = self.params["t1"]

        n0 = int(t0 * self.sample_rate)
        n1 = self.rir_len - int(t1 * self.sample_rate) - 1

        if n1 <= n0 + 4410:
            raise Exception("t0 should be less than t1")

        rir = k * self.pre_loaded_rir[n0:n1]

        lib = self.params["lib"]
        mode = self.params["mode"]
        method = self.params["method"]

        # convolve Room Impulse Response (RIR) with the sound
        if lib == "scipy":
            sound = signal.convolve(sound, rir, mode=mode, method=method)
        elif lib == "numpy":
            sound = np.convolve(sound, rir, mode=mode)

        return sound