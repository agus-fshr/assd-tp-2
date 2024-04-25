""" 
This module contains different parameter Objects that can be used to configure tools or modules from the application.

The parameters that can be used are:
- NumParam:     Numerical parameter with (interval) and (step)
- ChoiceParam:  Choice parameter with a list of strings (choices)
- BoolParam:    Boolean parameter

The parameters should be grouped in a ParameterList object. 
Each one can be accessed and modified by its name key using the [] operator of the ParameterList object

The parameter list is used to automatically generate a GUI for the user to interact with the parameters.

Each parameter will be displayed as:
- NumParam      ->  NumberInput (Slider + TextInput)
- ChoiceParam   ->  DropDownMenu
- BoolParam     ->  SwitchButton

 """

class ParameterBase():
    def __init__(self, name="parameter", text=""):
        self.internal_name = name
        self.text = text

    @property
    def name(self):
        return self.internal_name


class NumParam(ParameterBase):
    """ Numerical parameter with interval and step"""
    def __init__(self, name="x", interval=(0, 100), step=1, value=0, text="numerical parameter"):
        super().__init__(name, text)
        self.type = "Number"
        self.interval = interval
        self.step = step
        self.value = value

class ChoiceParam(ParameterBase):
    """ Choice parameter with a list of choices"""
    def __init__(self, name="y", options=["A", "B", "C"], value="A", text="choice parameter"):
        super().__init__(name, text)
        self.type = "Choice"
        self.options = options
        self.value = value

class BoolParam(ParameterBase):
    """ Boolean parameter"""
    def __init__(self, name="z", value=False, text="boolean parameter"):
        super().__init__(name)
        self.type = "Boolean"
        self.value = value


class ParameterList():
    """ List of parameters with unique names"""
    def __init__(self, *args):
        self.internal_parameter_list = {}
        
        # look for repeated names
        names = [p.name for p in list(args)]
        if len(names) != len(set(names)):
            raise ValueError("Repeated parameter names")
        
        for p in list(args):
            if not isinstance(p, ParameterBase):
                raise ValueError("All parameters must be of type ParameterBase")
            self.internal_parameter_list[p.name] = p

    def __len__(self):
        return len(self.internal_parameter_list)
    
    def keys(self):
        return self.internal_parameter_list.keys()
    
    def __iter__(self):
        values = self.internal_parameter_list.values()
        return iter(values)

    def __getitem__(self, key):
        if key not in self.internal_parameter_list:
            raise KeyError("Parameter not found")
        return self.internal_parameter_list[key].value
    
    def __setitem__(self, key, value):
        if key not in self.internal_parameter_list:
            raise KeyError(f"Parameter {key} not found")
        # if not isinstance(value, type(self.internal_parameter_list[key].v)):
        #     raise ValueError(f"Parameter {key} type mismatch. Expected {type(self.internal_parameter_list[key].step)}, got {type(value)}")
        self.internal_parameter_list[key].value = value