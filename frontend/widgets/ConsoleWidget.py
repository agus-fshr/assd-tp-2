from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from frontend.widgets.BasicWidgets import TextInput, Button

class ConsoleWidget(QWidget):
    def __init__(self, textSelectable=True, wordWrap=True, defaultText="Console output will appear here...", parent=None):
        super(ConsoleWidget, self).__init__(parent)
        
        self.defaultText = defaultText

        # Create the QLabel that will display the console output
        self.consoleOutput = QTextEdit()
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setWordWrapMode(wordWrap)
        self.consoleOutput.setFont(QFont("Monospace", 10))
        self.consoleOutput.setText(defaultText)
        self.consoleOutput.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        if textSelectable:
            self.consoleOutput.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.lineCount = QLabel("Lines: 0")
        
        # Create a QVBoxLayout for this widget and add the QScrollArea to it
        vlayout = QVBoxLayout(self)
        topHLayout = QHBoxLayout()
        topHLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        topHLayout.addWidget(self.lineCount)
        topHLayout.addStretch(1)
        topHLayout.addWidget(Button("Clear Console", on_click=lambda: self.setText(self.defaultText)))
        vlayout.addLayout(topHLayout)
        vlayout.addWidget(self.consoleOutput)
        
        # Set the layout for this widget
        self.setLayout(vlayout)
        
        # Additional styling or functionality can be added here as needed

    def setText(self, text):
        self.consoleOutput.setText(text)
        newlines = text.count('\n')+1
        self.lineCount.setText(f"Lines: {newlines}")

    def appendText(self, text):
        # Method to append text to the console, improving performance for large updates
        self.consoleOutput.moveCursor(Qt.QTextCursor.End)
        self.consoleOutput.insertPlainText(text)
        # Update line count
        newlines = self.consoleOutput.toPlainText().count('\n') + 1
        self.lineCount.setText(f"Lines: {newlines}")