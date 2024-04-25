from backend.ParamObject import NumParam, ChoiceParam, BoolParam, ParameterList
import numpy as np

from .EffectBaseClass import EffectBaseClass

class NoEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "No Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList()

    def process(self, sound):
        """ Apply no effect to the sound"""
        return sound


class DelayEffect(EffectBaseClass):
    def __init__(self):
        super().__init__()
        self.name = "Delay Effect" # Este nombre es el que se muestra en la interfaz

        # Estos son los parametros que se muestran en la interfaz y se pueden editar
        self.params = ParameterList(
            NumParam("delay", interval=(0, 1), value=0.18, step=0.01, text="Delay time [s]"),
            NumParam("feedback", interval=(0, 1), value=0.7, step=0.01, text="Feedback [0, 1]"),
        )

    def process(self, sound):
        """ Apply a delay effect to the sound """
        delay_time = self.params["delay"]
        feedback = self.params["feedback"]

        # Add zeros at the end of the sound array to allow for the delay effect
        sound = np.append(sound, np.zeros(int(5 * delay_time * self.sample_rate * (1/(1 - feedback*0.99)))))

        delay_samples = int(delay_time * self.sample_rate)
        delayed_sound = np.zeros(len(sound) + delay_samples)

        # Apply delay effect
        for i in range(len(sound)):
            delayed_sound[i + delay_samples] += sound[i] + feedback * delayed_sound[i]

        return delayed_sound