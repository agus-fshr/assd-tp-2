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
            NumParam("delay", interval=(0.001, 1), value=0.012, step=0.001, text="Delay time [s]"),
            NumParam("feedback", interval=(0.01, 1), value=0.99, step=0.01, text="Feedback [0, 1]"),
        )

    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = self.params["delay"]
        feedback = self.params["feedback"]
        active = self.params["active"]
        if not active:
            return sound

        # Add zeros at the end of the sound array to allow for the delay effect
        sound = np.append(sound, np.zeros(int(5 * delay_time * self.sample_rate * (1/(1 - feedback*0.9)))))

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

class LowPass_ReverbEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Lowpass Reverb Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("delay", interval=(0, 1.2), value=0.5, step=0.01, text="Delay time [s]"),
            NumParam("Duration", interval=(0, 8), value=1, step=0.1, text="Durantion [repetitions]"),
            # NumParam("atenuation", interval=(0, 0.99), value=0.5, step=0.01, text="Atenuation"),
            NumParam("Fb", interval=(25, 1000), value=500, step=1, text="Fb"),
        )
    
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = float(self.params["delay"])
        fb = float(self.params["Fb"])
        duratio = float(self.params["Duration"])
        # atenuation = float(self.params["atenuation"])
        active = self.params["active"]
        if not active:
            return sound
        
        delay_samples = int(delay_time * self.sample_rate) +1 
        
        #amplio el array
        new_sound = np.append(np.zeros(delay_samples), sound)
        new_sound = np.append(new_sound, np.zeros(int(duratio*delay_samples)))
        n = int(np.ceil((4*self.sample_rate) / fb))
        
        sound_out = np.zeros(len(new_sound)+delay_samples)
        impulse_lowpass = self.low_pass_filter(fb, n)
        
        for i in range(delay_samples, len(sound_out)):
            b = np.convolve(sound_out, impulse_lowpass, mode='valid')
            sound_out[i] = new_sound[i] + b[i - delay_samples]
        reverb_effect = sound_out[(2*delay_samples):]
        
        return reverb_effect

    #pasa bajos
    def low_pass_filter(self, fb, n):
        a1 = (np.tan(np.pi*fb/self.sample_rate)-1)/(np.tan(np.pi*fb/self.sample_rate)+1)
        x = np.zeros(n)
        x[0] = 1
        y = np.zeros(len(x))
        for i in range(1, len(x)):
            y[i] = a1*x[i] + x[i-1] - a1*y[i-1]
        low_pass_output = y

        return low_pass_output
    

class FlangerEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Flanger Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("delay", interval=(0, 15), value=10, step=0.1, text="Delay time [ms]"),
            NumParam("LFO frec", interval=(0, 1), value=0.5, step=0.01, text="LFO frec"),
            NumParam("LFO base", interval=(0.001, 2), value=2, step=0.001, text="LFO base"),
            NumParam("Gain", interval=(-0.99, 0.99), value=0.5, step=0.01, text="Feedback gain")
        )
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        active = self.params["active"]
        delay_time = float(self.params["delay"])/1000
        lfo_freq = float(self.params["LFO frec"])
        lfo_base = float(self.params["LFO base"])
        feedback_gain = float(self.params["Gain"])
        if not active:
            return sound
        length = len(sound)
        nsamples = np.array(range(length))
        
        
        sample_rate = int(np.around(delay_time*self.sample_rate))
        lfo = lfo_base + signal.sawtooth(2 * np.pi * lfo_freq * nsamples / self.sample_rate,0.5)
        cur_sin = np.abs(lfo)
        cur_delay = np.ceil(sample_rate*cur_sin)
        
        
        flanger_effect = np.zeros(length)
        for j in range(sample_rate+1, length):
            flanger_effect[j] = sound[j] + sound[j - int(cur_delay[j])]*feedback_gain
        return flanger_effect
    
class ChorusEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Chorus Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            BoolParam("active", value=False, text="Active"),
            NumParam("LFO frec 1", interval=(0, 10), value=1, step=0.01, text="LFO frec 1"),
            NumParam("LFO frec 2", interval=(0, 10), value=0.9, step=0.01, text="LFO frec 2"),
            NumParam("LFO frec 3", interval=(0, 10), value=0.8, step=0.01, text="LFO frec 3"),
            NumParam("LFO frec 4", interval=(0, 10), value=0.7, step=0.01, text="LFO frec 4"),
            NumParam("Gain", interval=(0, 0.99), value=0.7, step=0.01, text="Gain"),
            NumParam("Gain 1", interval=(-0.99, 0.99), value=0.6, step=0.01, text="Gain 1"),
            NumParam("Gain 2", interval=(-0.99, 0.99), value=0.5, step=0.01, text="Gain 2"),
            NumParam("Gain 3", interval=(-0.99, 0.99), value=0.4, step=0.01, text="Gain 3"),
            NumParam("Gain 4", interval=(-0.99, 0.99), value=0.3, step=0.01, text="Gain 4")
        )
    
    def process(self, sound):
        """ Apply a delay effect to the sound """
        active = self.params["active"]
        lfo_frec1 = float(self.params["LFO frec 1"])
        lfo_frec2 = float(self.params["LFO frec 2"])
        lfo_frec3 = float(self.params["LFO frec 3"])
        lfo_frec4 = float(self.params["LFO frec 4"])
        gain = float(self.params["Gain"])
        gain1 = float(self.params["Gain 1"])
        gain2 = float(self.params["Gain 2"])
        gain3 = float(self.params["Gain 3"])
        gain4 = float(self.params["Gain 4"])
        if not active:
            return sound
        length = len(sound)
        nsamples = np.array(range(length))
        
        
        time_delay = 0.025
        rate = [lfo_frec1, lfo_frec2, lfo_frec3, lfo_frec4]
        nb_effect = len(rate)
        
        amp = [gain1, gain2, gain3, gain4]
        
        
        sin_ref = np.array([np.sin(2*np.pi*nsamples*(rate[j]/self.sample_rate)) for j in range(nb_effect)])
        
        max_sample_delay = int(np.around(time_delay*self.sample_rate))
        chorus_effect = np.zeros(length)
        for i in range(max_sample_delay):
            chorus_effect[i] = sound[i]
        
        cur_sin = np.abs(sin_ref)
        cur_delay = np.ceil(max_sample_delay*cur_sin)
        for i in range(max_sample_delay + 1, length):
            chorus_effect[i] = gain*sound[i] + amp[0]*sound[i-int(cur_delay[0][i])] + amp[1]*sound[i-int(cur_delay[1][i])] 
            + amp[2]*sound[i-int(cur_delay[2][i])] + amp[3]*sound[i-int(cur_delay[3][i])]
        
        return chorus_effect

    

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