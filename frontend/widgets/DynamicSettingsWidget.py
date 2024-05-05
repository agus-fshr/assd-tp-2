from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .BasicWidgets import SwitchButton, NumberInput, DropDownMenu, TextInput

class DynamicSettingsWidget(QWidget):
    def __init__(self, paramList=None, title="Dynamic Settings", on_edit=lambda: None):
        super().__init__()
        self.paramList = paramList
        self.on_edit = on_edit
        self.title = title
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.initUI()

    def initUI(self):
        self.dynamicLayout = QVBoxLayout()
        self.dynamicLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.dynamicLayout.setContentsMargins(0, 0, 0, 0)
        self.dynamicLayout.setSpacing(0)

        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        hlayout.addLayout(self.dynamicLayout)

        # Create a new widget for the scroll area
        scroll_widget = QWidget()
        scroll_widget.setLayout(hlayout)
        scroll_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Create a scroll area and set its widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_widget)
        self.scroll_area.setMinimumHeight(250)
        self.scroll_area.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        self.updateUI(self.paramList)

    def updateUI(self, paramList, title="Dynamic Settings"):
        self.paramList = paramList
        while self.dynamicLayout.count():
            child = self.dynamicLayout.takeAt(0)
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
        font = QFont("Arial", 14, QFont.Bold)
        titleLabel.setFont(font)
        self.dynamicLayout.addWidget(titleLabel)

        if self.paramList is None:
            return

        max_widget_width = titleLabel.sizeHint().width() + titleLabel.frameWidth() * 2
        for param in self.paramList:
            key = param.name
            
            settingWidget = None
            if param.type == "Boolean":
                settingWidget = SwitchButton(param.text + " On", param.text + " Off", 
                                      on_click=lambda v, k=key: self.on_param_set(k, v), value=param.value)

            elif param.type == "Number":
                settingWidget = NumberInput(param.text, interval=param.interval, step=param.step, default=param.value, 
                                     on_change= lambda v, k=key: self.on_param_set(k, v))
            
            elif param.type == "Choice":
                opt_dict = {}
                for opt in param.options:
                    opt_dict[opt] = opt

                settingWidget = QWidget()
                dropLayout = QHBoxLayout()
                dropLayout.addWidget(QLabel(param.text + ": "))
                dropLayout.addWidget(DropDownMenu(self.paramList[key], options=opt_dict, 
                                      onChoose=lambda v, _, k=key: self.on_param_set(k, v)))
                settingWidget.setLayout(dropLayout)

            elif param.type == "text":
                settingWidget = TextInput(param.text, 
                                          on_change=lambda v, k=key: self.on_param_set(k, v),
                                          default=param.value,
                                          regex="^$|^[a-zA-Z0-9\\*\\+\\-\\^\\/\\(\\)\\s\\.]*")
            else:
                raise ValueError(f"Parameter type '{param.type}' not recognized")
            
            current_width = settingWidget.sizeHint().width()
            if hasattr(settingWidget, "frameWidth"):
                current_width += settingWidget.frameWidth() * 2
            max_widget_width = max(max_widget_width, current_width)
            self.dynamicLayout.addWidget(settingWidget)

        # Resize the scroll area to fit the new content
        margins = self.dynamicLayout.contentsMargins().left() + self.dynamicLayout.contentsMargins().right()
        frameWidth = self.scroll_area.frameWidth()
        barWidth = self.scroll_area.verticalScrollBar().sizeHint().width()
        scroll_width = int(max_widget_width*1.1) + 2*frameWidth + barWidth + margins
        self.scroll_area.setMinimumWidth(scroll_width)

    def on_param_set(self, key, value):
        self.paramList[key] = value
        self.on_edit()