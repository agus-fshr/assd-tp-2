import numpy as np


#   FUNCTION MODULATOR
class ModFunction():
    def __init__(self, type="linear", n=1.0):
        if n < 0.1 or n > 20:
            raise ValueError("ModFunction n must be between 0.1 and 20")
        
        match type:
            case "linear":
                self.func = lambda x: x
            case "exp":
                self.func = lambda x: (np.exp(n*x) - 1) / (np.exp(n) - 1)
            case "log":
                self.func = lambda x: np.log(n*x + 1) / np.log(n + 1)
            case "poly":
                self.func = lambda x: x**n
            case "polyFlatTop":
                self.func = lambda x: 1 - (1 - x)**n
            case "sin":
                self.func = lambda x: (np.sin(x * np.pi / 2)) ** n
            case "cos":
                self.func = lambda x: 1 - (np.cos(x * np.pi / 2)) ** n


    def __call__(self, x):
        if np.min(x) < 0.0 or np.max(x) > 1.0:
            raise ValueError("Call Input value must be between 0 and 1")
        return self.func(x)


    def mod(self, x, x0=0.0, x1=0.0, y0=0.0, y1=0.0):
        """ Modulate a value x between x0 and x1 to a value between y0 and y1"""
        if np.min(x) < x0 or np.max(x) > x1:
            raise ValueError("Mod Input value must be between x0 and x1")
        return y0 + (y1 - y0) * self((x - x0) / (x1 - x0))





class LinearADSR():
    def __init__(self, k, A, D, R, tone_duration, modType="polyFlatTop", n=3.0):
        self.k = k
        self.attack = A
        self.decay = D
        self.release = R
        self.tone_duration = tone_duration

        self.attackFunction = ModFunction(modType, n)
        self.decayFunction = ModFunction(modType, n)
        self.releaseFunction = ModFunction(modType, n)

        points = int((self.tone_duration + R) * 44100)
        self.t = np.linspace(0, self.tone_duration + R, points, endpoint=False)

    def time(self):
        return self.t

    def envelope(self):
        """ Generate the ADSR envelope for a given time array t and note duration
        t: numpy array of time values
        duration: total duration of the note in seconds (from on to off)
        """
        # Calculate the sustain phase duration

        k = self.k
        A = self.attack
        D = self.decay
        R = self.release
        t = self.t
        
        if self.tone_duration < A + D:
            self.tone_duration = A + D
        S = self.tone_duration - self.attack - self.decay        

        # Create an output array of the same shape as t
        output = np.zeros_like(t)
        

        # Attack phase
        attack_mask = t < A
        output[attack_mask] = self.attackFunction.mod(t[attack_mask], x1=A, y1=k)
        
        # Decay phase
        decay_mask = (t >= A) & (t < A + D)
        output[decay_mask] = self.decayFunction.mod(t[decay_mask], x0=A, x1=A+D, y0=k*1, y1=1)
        
        # Sustain phase
        sustain_mask = (t >= A + D) & (t < A + D + S)
        output[sustain_mask] = 1.0
        
        # Release phase
        release_mask = (t >= A + D + S) & (t < A + D + S + R)
        output[release_mask] = self.releaseFunction.mod(t[release_mask], x0=A+D+S, x1=A+D+S+R, y0=1, y1=0)
                
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