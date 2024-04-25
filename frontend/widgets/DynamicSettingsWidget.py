from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .BasicWidgets import SwitchButton, NumberInput, DropDownMenu

class DynamicSettingsWidget(QWidget):
    def __init__(self, paramList=None, title="Dynamic Settings", on_edit=lambda: None):
        super().__init__()
        self.paramList = paramList
        self.on_edit = on_edit
        self.title = title
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        hlayout.addLayout(self.layout)
        hlayout.addStretch(1)
        
        self.setLayout(hlayout)
        self.updateUI(self.paramList)

    def updateUI(self, paramList, title="Dynamic Settings"):
        self.paramList = paramList
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            if child.layout():
                while child.layout().count():
                    grandchild = child.layout().takeAt(0)
                    if grandchild.widget():
                        grandchild.widget().deleteLater()
                    if grandchild.layout():
                        while grandchild.layout().count():
                            grandgrandchild = grandchild.layout().takeAt(0)
                            if grandgrandchild.widget():
                                grandgrandchild.widget().deleteLater()
        
        titleLabel = QLabel(title)
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.layout.addWidget(titleLabel)

        if self.paramList is None:
            return
        for param in self.paramList:
            key = param.name
            
            widget = None
            if param.type == "Boolean":
                widget = SwitchButton(param.text + " On", param.text + " Off", 
                                      on_click=lambda v, k=key: self.on_param_set(k, v), value=param.value)

            elif param.type == "Number":
                widget = NumberInput(param.text, interval=param.interval, step=param.step, default=param.value, 
                                     on_change= lambda v, k=key: self.on_param_set(k, v))
            
            elif param.type == "Choice":
                opt_dict = {}
                for opt in param.options:
                    opt_dict[opt] = opt

                widget = QWidget()
                dropLayout = QHBoxLayout()
                dropLayout.addWidget(QLabel(param.text + ": "))
                dropLayout.addWidget(DropDownMenu(self.paramList[key], options=opt_dict, 
                                      onChoose=lambda v, _, k=key: self.on_param_set(k, v)))
                widget.setLayout(dropLayout)
            
            
            self.layout.addWidget(widget)
        self.layout.addStretch(1)

    def on_param_set(self, key, value):
        self.paramList[key] = value
        self.on_edit()