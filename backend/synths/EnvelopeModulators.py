import numpy as np

class LinearADSR():
    def __init__(self, amp, k, A, D, R):
        self.A = amp
        self.k = k
        self.attack = A
        self.decay = D
        self.release = R


    def __call__(self, t, tone_duration):
        """ Generate the ADSR envelope for a given time array t and note duration
        t: numpy array of time values
        duration: total duration of the note in seconds (from on to off)
        """
        # Calculate the sustain phase duration
        S = tone_duration - self.attack - self.decay

        # Create an output array of the same shape as t
        output = np.zeros_like(t)
        
        # Attack phase
        attack_mask = t < self.attack
        output[attack_mask] = self.A * (t[attack_mask] / self.attack) * self.k
        
        # Decay phase
        decay_mask = (t >= self.attack) & (t < self.attack + self.decay)
        output[decay_mask] = self.A * (self.k - (self.k - 1) * (t[decay_mask] - self.attack) / self.decay)
        
        # Sustain phase
        sustain_mask = (t >= self.attack + self.decay) & (t < self.attack + self.decay + S)
        output[sustain_mask] = self.A
        
        # Release phase
        release_mask = (t >= self.attack + self.decay + S) & (t < self.attack + self.decay + S + self.release)
        output[release_mask] = self.A * (1 - (t[release_mask] - self.attack - self.decay - S) / self.release)
                
        return output
    
class WoodwindEnvelope():
    def __init__(self, amp, k, A, D, R):
        self.A = amp
        self.k = k
        self.attack = A
        self.decay = D
        self.release = R




    def __call__(self, t, tone_duration):
        """ Generate the ADSR envelope for a given time array t and note duration
        t: numpy array of time values
        duration: total duration of the note in seconds (from on to off)
        """
        # Calculate the sustain phase duration
        S = tone_duration - self.attack - self.decay

        # Create an output array of the same shape as t
        output = np.zeros_like(t)
        
        # Attack phase 1
        attack_mask = t < (self.attack)
        output[attack_mask] = self.A * (t[attack_mask] / self.attack)**2 * self.k

        # Decay phase
        decay_mask = (t >= self.attack) & (t < self.attack + self.decay)
        output[decay_mask] = self.A * (self.k - (self.k - 1) * (t[decay_mask] - self.attack) / self.decay)
        
        # Sustain phase
        sustain_mask = (t >= self.attack + self.decay) & (t < self.attack + self.decay + S)
        output[sustain_mask] = self.A
        
        # Release phase
        release_mask = (t >= self.attack + self.decay + S) & (t < self.attack + self.decay + S + self.release)
        output[release_mask] = self.A * (1 - (t[release_mask] - self.attack - self.decay - S) / self.release)
                
        return output
    

class WoodwindModEnvelope():
    def __init__(self, amp, k, A, D, R, k2d,sfval):
        self.A = amp
        self.k = k
        self.attack = A
        self.decay = D
        self.release = R
        self.k2d = k2d #linear attack duration [0;1], as a fraction of A
        self.sfval = sfval #final value at sustain time as a fraction



    def __call__(self, t, tone_duration):
        """ Generate the ADSR envelope for a given time array t and note duration
        t: numpy array of time values
        duration: total duration of the note in seconds (from on to off)
        """
        # Calculate the sustain phase duration
        S = tone_duration - self.attack - self.decay

        # Create an output array of the same shape as t
        output = np.zeros_like(t)
        
        # Attack phase 1
        attack_mask = t < (self.attack * self.k2d)
        output[attack_mask] = self.A * (t[attack_mask] / self.attack) * self.k
        # Attack phase 2

        ConstanteB = ((self.A * self.k)/((self.A * self.k * self.k2d)**(1/self.k2d)))**(1/(1-1/self.k2d))
        ConstanteC = np.log(self.A * self.k* self.k2d/ConstanteB)/(self.attack * self.k2d)
        attack_mask2 = (t >= (self.attack*self.k2d)) & (t < self.attack)
        output[attack_mask2] = ConstanteB*np.exp(ConstanteC*t[attack_mask2])
        
        # Decay phase
        decay_mask = (t >= self.attack) & (t < self.attack + self.decay)
        output[decay_mask] = self.A * (self.k - (self.k - 1) * (t[decay_mask] - self.attack) / self.decay)
        
        # Sustain phase
        sustain_mask = (t >= self.attack + self.decay) & (t < self.attack + self.decay + S)
        output[sustain_mask] = self.A + (self.sfval - 1)* (t[sustain_mask]/S)
        
        # Release phase
        release_mask = (t >= self.attack + self.decay + S) & (t < self.attack + self.decay + S + self.release)
        output[release_mask] = self.A * (1 - (t[release_mask] - self.attack - self.decay - S) / self.release)
                
        return output