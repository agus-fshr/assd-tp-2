from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QLineEdit, QWidget, QSlider, QPushButton
from PyQt5.QtGui import QColor, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp

# Button class
class Button(QPushButton):

    def __init__(self, text="Click Me", color="black", background_color = "white", 
                        radius=10,
                        shadow_color="grey", shadow_radius=9, hover_color="lightblue", 
                        click_color="grey", padding=6, on_click=lambda: print("Button Clicked")):
        super().__init__(text)

        self.setStyleSheet(f"""
            QPushButton {{ 
                color: {color};
                background-color: {background_color};
                border-radius: {radius}px;                
                padding: {padding}px;
            }}""" +

        f"""
            QPushButton:hover {{
                background-color: {hover_color};
                border-radius: {radius}px;
                padding: {padding}px;
            }}

            QPushButton:pressed {{
                background-color: {click_color};
                border-radius: {radius}px;
                padding: {padding}px;
            }}
        """)

        self.clicked.connect(self.on_click_callback)

        self.on_click = on_click

        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(shadow_color))
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(shadow_radius)
        self.setGraphicsEffect(shadow)

    def on_click_callback(self):
        self.on_click()


# Text Input class
class TextInput(QWidget):
    def __init__(self, label="Input", placeholder="Type Here", on_change=lambda text: (), regex="[a-zA-Z0-9\-\.]*"):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.label = QLabel(label)
        self.textbox = QLineEdit(self)
        self.textbox.setPlaceholderText(placeholder)
        if regex:
            validator = QRegExpValidator(QRegExp(regex))
            self.textbox.setValidator(validator)

        layout.addWidget(self.label)
        layout.addWidget(self.textbox)

        self.setLayout(layout)

        self.textbox.textChanged.connect(self.on_change_callback)

        self.on_change = on_change

    def text(self):
        return self.textbox.text()

    def on_change_callback(self, text):
        self.on_change(text)


class Slider(QWidget):
    def __init__(self, label="Slider", range=(0, 100), step=1, on_change=lambda value: (), minWidth=200):
        super().__init__()

        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.label = QLabel(label)
        self.displayValue = QLabel(" = " + str(range[0]))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(range[0])
        self.slider.setMaximum(range[1])
        self.slider.setSingleStep(step)
        self.slider.setMinimumWidth(minWidth)

        hlayout.addWidget(self.label)
        hlayout.addWidget(self.displayValue)
        hlayout.addStretch(1)

        layout.addLayout(hlayout)
        layout.addWidget(self.slider)

        self.setLayout(layout)

        self.slider.valueChanged.connect(self.on_change_callback)

        self.on_change = on_change

    def value(self):
        return self.slider.value()

    def on_change_callback(self, value):
        self.displayValue.setText(" = " + str(value))
        self.on_change(value)