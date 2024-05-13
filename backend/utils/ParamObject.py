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
- TextParam     ->  TextInput

 """

import sympy as sp
import numpy as np

class ParameterBase():
    def __init__(self, name="parameter", text=""):
        self.internal_name = name
        self.text = text

    @property
    def name(self):
        return self.internal_name


class TextParam(ParameterBase):
    """ Text parameter with a string"""
    def __init__(self, name="txt", value="", text="text parameter", default=None):
        super().__init__(name, text)
        self.type = "text"
        if default is not None:
            self.value = default
        else:
            self.value = value


class NumParam(ParameterBase):
    """ Numerical parameter with interval and step"""
    def __init__(self, name="x", interval=(0, 100), step=1, value=0, text="numerical parameter", default=None):
        super().__init__(name, text)
        self.type = "Number"
        self.interval = interval
        self.step = step
        if default is not None:
            self.value = default
        else:
            self.value = value

class ChoiceParam(ParameterBase):
    """ Choice parameter with a list of choices"""
    def __init__(self, name="y", options=["A", "B", "C"], value="A", text="choice parameter", default=None):
        super().__init__(name, text)
        self.type = "Choice"
        self.options = options
        if default is not None:
            self.value = default
        else:
            self.value = value


class BoolParam(ParameterBase):
    """ Boolean parameter"""
    def __init__(self, name="z", value=False, text="boolean parameter", default=None):
        super().__init__(name, text)
        self.type = "Boolean"
        if default is not None:
            self.value = default
        else:
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
        params = self.internal_parameter_list.values()
        return iter(params)

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



    def getFunction(self, eq, var, const = {}):
        '''
        If a TextParam is a valid equation, this function returns a lambda function that can be used to evaluate the equation with a given variable, the exising parameters and constants.
        - eq: name of the TextParam that contains the equation
        - var: name of the variable to be used in the equation (is not needed to be present in the equation)
        - const: dictionary with constant values (optional)
        '''
        eqstr = self[eq]
        try:
            eq = sp.sympify(eqstr)
        except Exception as e:
            raise ValueError(f"Error parsing equation: {eqstr}")            
        
        if var in const.keys():
            raise ValueError(f"Variable {var} is also a constant")
        if var in self.keys():
            raise ValueError(f"Variable {var} is also a parameter")

        # Substitute constants and parameters
        for symbol in eq.free_symbols:
            if symbol.name in self.keys():
                eq = eq.subs(symbol, self[symbol.name])
            elif symbol.name in const.keys():
                eq = eq.subs(symbol, const[symbol.name])

        if len(eq.free_symbols) > 1:
            raise ValueError(f"Equation '{eqstr}' has more than one free symbols: {eq.free_symbols}")

        if len(eq.free_symbols) == 0:
            return lambda x: complex(eq.evalf())
        

        eq = eq.simplify()
        x = eq.free_symbols.pop()

        # Lambdify the equation
        func = sp.lambdify(x, eq, "numpy")
        return func