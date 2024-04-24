

class Param():
    def __init__(self, value=0.0, interval=(0.0, 1.0), name="Parameter", steps=100):
        self.value = value
        self.interval = interval
        self.name = name
        self.steps = steps

    def slider_range(self):
        return (self.interval[0]*self.steps, self.interval[1]*self.steps)