from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QLineEdit, QWidget, QSlider, QPushButton, QMenu, QAction
from PyQt5.QtGui import QColor, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
import numpy as np

# Button class
class Button(QPushButton):

    def __init__(self, text="Click Me", color="black", background_color = "white", 
                        radius=10,
                        shadow_color="grey", shadow_radius=9, hover_color="lightblue", 
                        click_color="grey", padding=6, on_click=None):
        super().__init__(text)
        self.radius = radius
        self.padding = padding

        self.setColors(color, background_color, hover_color, click_color)

        if isinstance(on_click, pyqtSignal):
            self.clicked.connect(on_click)
        elif callable(on_click):
            self.clicked.connect(self.on_click_callback)
            self.on_click = on_click

        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(shadow_color))
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(shadow_radius)
        self.setGraphicsEffect(shadow)

    def setColors(self, color, background_color, hover_color, click_color):
        self.setStyleSheet(f"""
            QPushButton {{ 
                color: {color};
                background-color: {background_color};
                border-radius: {self.radius}px;                
                padding: {self.padding}px;
            }}""" +

        f"""
            QPushButton:hover {{
                background-color: {hover_color};
                border-radius: {self.radius}px;
                padding: {self.padding}px;
            }}

            QPushButton:pressed {{
                background-color: {click_color};
                border-radius: {self.radius}px;
                padding: {self.padding}px;
            }}
        """)

    def on_click_callback(self):
        self.on_click()


class SwitchButton(Button):
    def __init__(self, text_on="On", text_off="Off", color_on="white", color_off="black",
                 background_color_on="green", background_color_off="red",
                 radius=10, shadow_color="grey", shadow_radius=9, hover_color="lightgrey",
                 click_color="grey", padding=6, on_click=lambda is_on: print("Button Toggled", is_on), value=False):
        # Initialize with the "off" state appearance
        super().__init__(text=text_off, color=color_off, background_color=background_color_off,
                         radius=radius, shadow_color=shadow_color, shadow_radius=shadow_radius,
                         hover_color=hover_color, click_color=click_color, padding=padding, on_click=on_click)
        self.text_on = text_on
        self.text_off = text_off
        self.color_on = color_on
        self.color_off = color_off
        self.hover_color = hover_color
        self.click_color = click_color
        self.background_color_on = background_color_on
        self.background_color_off = background_color_off
        self.value = value
        self.set_value(value)

    def set_value(self, value):
        self.value = value
        # Update the button's appearance based on the new state
        if value:
            self.setText(self.text_on)
            self.setColors(self.color_on, self.background_color_on, self.hover_color, self.click_color)
        else:
            self.setText(self.text_off)
            self.setColors(self.color_off, self.background_color_off, self.hover_color, self.click_color)

    def on_click_callback(self):
        self.set_value(not self.value)
        self.on_click(self.value)


# Text Input class
class TextInput(QWidget):
    def __init__(self, label="Input", placeholder="Type Here", default="", on_change=lambda text: (), regex="^$|[a-zA-Z0-9\\-\\.]*", layout='v', callOnEnter=True):
        super().__init__()

        if layout == 'h':
            layout = QHBoxLayout()
        elif layout == 'v':
            layout = QVBoxLayout()
        else:
            raise ValueError("Invalid layout parameter. Use 'h' for horizontal or 'v' for vertical layout.")
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.label = QLabel(label)
        self.textbox = QLineEdit(self)
        self.textbox.setPlaceholderText(placeholder)
        self.textbox.setText(default)
        if regex:
            validator = QRegExpValidator(QRegExp(regex))
            self.textbox.setValidator(validator)

        layout.addWidget(self.label)
        layout.addWidget(self.textbox)

        self.setLayout(layout)

        if callOnEnter:
            self.textbox.returnPressed.connect(self.on_change_callback)
        else:
            self.textbox.textEdited.connect(self.on_change_callback)

        self.on_change = on_change

    def text(self):
        return self.textbox.text()

    def on_change_callback(self):
        self.on_change(self.textbox.text())


# Horizontal Slider Class
class Slider(QWidget):
    def __init__(self, label="Slider", interval=(0, 100), step=1, defaultVal=0, on_change=lambda value: None, minWidth=100):
        super().__init__()

        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Set the slider values
        self.interval = interval
        self.delta = interval[1] - interval[0]
        self.integer = isinstance(self.delta, int) and isinstance(defaultVal, int) and (step == 1)
        self.start = interval[0]
        if self.integer:
            self.max_index = self.delta
            self.decimals = 0
        else:
            self.max_index = int(np.ceil(self.delta / step))
            self.decimals = int(np.ceil(np.log10(1.0 / step)))
        self.current_value = defaultVal

        # Set the label
        self.label = QLabel(label)
        self.displayValue = QLabel(" = " + str(round(defaultVal, self.decimals)) )

        # Create the slider
        self.slider = QSlider(Qt.Horizontal)
        if self.integer:
            self.slider.setMinimum(interval[0])
            self.slider.setMaximum(interval[1])
        else:
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.max_index)
        self.slider.setValue(self.value_to_slider_pos(self.current_value))
        self.slider.setSingleStep(1)
        self.slider.setMinimumWidth(minWidth)

        hlayout.addWidget(self.label)
        hlayout.addWidget(self.displayValue)
        hlayout.addStretch(1)

        layout.addLayout(hlayout)
        layout.addWidget(self.slider)

        self.setLayout(layout)

        self.slider.valueChanged.connect(self.on_change_callback)

        self.on_change = on_change

    def value_to_slider_pos(self, value):
        if self.integer:
            return int(value)
        pos = ((value - self.start) / self.delta) * self.max_index
        return int(np.clip(pos, 0, self.max_index))

    def slider_pos_to_value(self, pos):
        if self.integer:
            return int(pos)
        return self.start + (pos / self.max_index) * self.delta

    def value(self):
        return self.slider_pos_to_value(self.slider.value())

    def on_change_callback(self, pos):
        value = self.slider_pos_to_value(pos)
        self.displayValue.setText(" = " + self.value_to_text(value) )
        self.on_change(value)

    def value_to_text(self, value):
        if self.integer:
            return str(value)
        return str(round(value, self.decimals))




# Number Input class
class NumberInput(QWidget):
    def __init__(self, label="Number", interval=(0, 100), step=1, default=0, on_change=lambda value: None, minWidth=100, callOnEnter=True, sliderRelease=True):
        super().__init__()
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Set the value range
        self.interval = interval
        self.delta = interval[1] - interval[0]
        self.integer = isinstance(self.delta, int) and isinstance(default, int) and (step == 1)
        self.start = interval[0]
        if self.integer:
            self.max_index = self.delta
            self.decimals = 0
        else:
            self.max_index = int(np.ceil(self.delta / step))
            self.decimals = int(np.ceil(np.log10(1.0 / step)))
        self.current_value = default

        # Set the Label and TextBox
        self.label = QLabel(label + " = ")
        self.textbox = QLineEdit()
        if self.integer:
            self.textbox.setValidator(QRegExpValidator(QRegExp("^$|[+-]?[0-9]+")))
        else:
            self.textbox.setValidator(QRegExpValidator(QRegExp("^$|[+-]?[0-9]+(?:\\.[0-9]+)?")))
        self.textbox.setText(str(round(self.current_value, self.decimals)))

        # Create the slider
        self.slider = QSlider(Qt.Horizontal)
        if self.integer:
            self.slider.setMinimum(interval[0])
            self.slider.setMaximum(interval[1])
        else:
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.max_index)
        self.slider.setValue(self.value_to_slider_pos(self.current_value))
        self.slider.setSingleStep(1)
        self.slider.setMinimumWidth(minWidth)


        hlayout.addWidget(self.label)
        hlayout.addWidget(self.textbox)
        layout.addLayout(hlayout)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        if callOnEnter:
            self.textbox.returnPressed.connect(self.on_text_change)
        else:
            self.textbox.textEdited.connect(self.on_text_change)

        if sliderRelease:
            self.slider.sliderReleased.connect(self.on_slider_change)
        else:
            self.slider.valueChanged.connect(self.on_slider_change)

        self.on_change = on_change

    def on_slider_change(self):
        pos = self.slider.value()
        self.current_value = self.slider_pos_to_value(pos)
        self.textbox.blockSignals(True)
        self.textbox.setText(self.value_to_text(self.current_value))
        self.textbox.blockSignals(False)
        self.on_change(self.current_value)

    def on_text_change(self):
        text = self.textbox.text()
        if text == "":
            self.textbox.setText(self.value_to_text(self.current_value))
            return
        
        value = 0.0
        try:
            value = float(text) # try to convert the text to a float
        except ValueError as e:
            print(f"Error: {e}")
            self.textbox.blockSignals(True)
            self.textbox.setText(self.value_to_text(self.current_value))
            self.textbox.blockSignals(False)
            return
        
        resetTextValue = False
        if value < self.interval[0]:
            self.current_value = self.interval[0]
            resetTextValue = True
        if value > self.interval[1]:
            self.current_value = self.interval[1]
            resetTextValue = True

        if resetTextValue:
            self.textbox.blockSignals(True)
            self.textbox.setText(self.value_to_text(self.current_value))
            self.textbox.blockSignals(False)
        else:
            self.current_value = value

        self.slider.blockSignals(True)
        self.slider.setValue(self.value_to_slider_pos(self.current_value))
        self.slider.blockSignals(False)
        
        self.on_change(self.current_value)


    def value(self):
        return self.current_value
    
    def value_to_slider_pos(self, value):
        if self.integer:
            return int(value)
        pos = ((value - self.start) / self.delta) * self.max_index
        return int(np.clip(pos, 0, self.max_index))

    def slider_pos_to_value(self, pos):
        if self.integer:
            return int(pos)
        return self.start + (pos / self.max_index) * self.delta
    
    def value_to_text(self, value):
        if self.integer:
            return str(value)
        return str(round(value, self.decimals))





class DropDownMenu(Button):
    """
    A custom DropDown Menu class

    Attributes:
        - title (str): The default title of the dropdown menu.
        - showSelected (bool): Flag to show the selected option as the button text.
        - onChoose (function): Callback function to execute when an option is chosen, it receives the key of the chosen option.
        - options (dict): A dictionary of options where keys are option labels and values are whatever you want.
    
    Structure of the options dictionary:
    
    """
    def __init__(self, title = "Select", showSelected = True, onChoose = lambda x: None, options={}, firstSelected=False):
        super(DropDownMenu, self).__init__(title)
        self.onChoose = onChoose
        self.selected = None
        self.selected_title = None
        self.showSelected = showSelected
        self.is_list = False
        self.is_widget = False
        self.options = options
        self.menu = QMenu(self)
        self.setMenu(self.menu)
        self.set_options(options, firstSelected)
        self.menu.setStyleSheet("""
            QMenu::item:selected {
                background-color: lightblue;
                color: black;
            }
            QMenu::item {
                background-color: white;
                color: black;
            }
        """)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
        else:
            super().keyPressEvent(event)


    def set_options(self, options={}, firstSelected=False):
        # release previous connected actions
        for action in self.menu.actions():
            action.triggered.disconnect()
        self.menu.clear()

        self.is_list = True if isinstance(options, list) else False     # check if list
        if self.is_list and len(options) > 0:
            self.is_widget = isinstance(options[0], QWidget)            # check QWidget
        self.options = options

        if self.is_widget:
            if not hasattr(options[0], "title"):
                raise Exception("DropDownMenu: First element of the list is a QWidget but it doesn't have a 'title' attribute")


        if len(options) > 0 and firstSelected:
            if self.is_list:
                if self.is_widget:
                    self.selected_title = options[0].title
                else:
                    self.selected_title = options[0]

                if self.showSelected:
                    self.setText(self.selected_title)
                self.selected = options[0]  # text or widget
            else:
                self.selected_title = list(options.keys())[0]
                self.selected = options[self.selected_title]
                self.setText(self.selected_title)

        # create new actions
        if self.is_list:
            iterator = options
        else:
            iterator = options.keys()
        for key in iterator:
            if self.is_widget:
                action = QAction(key.title, self)
            else:
                action = QAction(key, self)
            action.triggered.connect(lambda _, k=key: self.call_selected_option(k))
            self.menu.addAction(action)

    def call_selected_option(self, key):
        if self.is_list:
            self.selected = key
            if self.is_widget:
                self.selected_title = key.title
            else:
                self.selected_title = key
            self.onChoose(key)
        else:
            self.selected = self.options[key]
            self.selected_title = key
            self.onChoose(key, self.options[key])

        if self.showSelected:
            self.setText(self.selected_title)