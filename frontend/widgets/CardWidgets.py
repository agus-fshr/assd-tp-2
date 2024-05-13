# CardWidget, CardListWidget

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QStyle, QHBoxLayout, QToolButton, QScrollArea, QFrame
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt

class ContainerWidget(QWidget):
    def __init__(self, child=None, children=None, layoutType=QHBoxLayout(), shadow=True, borderRadius=10, backgroundColor="#aaaaaa"):
        super(ContainerWidget, self).__init__()

        self.containerLayout = layoutType
        self.containerLayout.setContentsMargins(10, 10, 10, 10)
        self.containerLayout.setSpacing(10)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {backgroundColor};
                border-radius: {borderRadius}px;
            }}
        """)

        # Set up the shadow effect for the container widget
        if shadow:
            shadowEffect = QGraphicsDropShadowEffect()
            shadowEffect.setBlurRadius(15)
            shadowEffect.setColor(QColor(0, 0, 0, 80))
            shadowEffect.setXOffset(0)
            shadowEffect.setYOffset(4)
            self.setGraphicsEffect(shadowEffect)

        if isinstance(child, QWidget):
            self.containerLayout.addWidget(child)
        if isinstance(child, QVBoxLayout) or isinstance(child, QHBoxLayout):
            self.containerLayout.addLayout(child)
        if isinstance(children, list):
            for child in children:
                if isinstance(child, QWidget):
                    self.containerLayout.addWidget(child)
                if isinstance(child, QVBoxLayout) or isinstance(child, QHBoxLayout):
                    self.containerLayout.addLayout(child)

        wrapperWidget = QWidget()
        wrapperWidget.setLayout(self.containerLayout)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(wrapperWidget)
        self.setLayout(mainLayout)

    def addWidget(self, widget):
        if isinstance(widget, QWidget):
            self.containerLayout.addWidget(widget)
        if isinstance(widget, list):
            for w in widget:
                if isinstance(w, QWidget):
                    self.containerLayout.addWidget(w)


class CardWidget(QWidget):
    def __init__(self, child=None, children=None, title="Card", subtitle="", width=None, height=None, iconSize=64, icon=QStyle.SP_DriveCDIcon, titleFont=QFont('Arial', 16, QFont.Bold), subtitleFont=None):
        super(CardWidget, self).__init__()
        
        # Use a standard icon
        iconLabel = QLabel()
        icon = self.style().standardIcon(icon)
        pixmap = icon.pixmap(iconSize, iconSize)
        iconLabel.setPixmap(pixmap)
        iconLabel.setAlignment(Qt.AlignCenter)
        
        # Main Title

        titlesLayout = QVBoxLayout()
        titleLabel = QLabel(title)
        if isinstance(titleFont, QFont):
            titleLabel.setFont(titleFont)
        titleLabel.setAlignment(Qt.AlignLeft)
        subtitleLabel = QLabel(subtitle)
        if isinstance(subtitleFont, QFont):
            subtitleLabel.setFont(subtitleFont)
        subtitleLabel.setAlignment(Qt.AlignLeft)
        titlesLayout.addWidget(titleLabel)
        titlesLayout.addWidget(subtitleLabel)
                
        # Container widget
        container = ContainerWidget(children=[iconLabel, titlesLayout, child])

        
        # Main layout for the widget
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(container)
        self.setLayout(mainLayout)

        # Set fixed size for the whole widget
        if width is not None and height is not None:
            self.setFixedSize(width, height)  # Example fixed size
        elif width is not None:
            self.setFixedWidth(width)
        elif height is not None:
            self.setFixedHeight(height)        





class CardListWidget(QWidget):
    def __init__(self):
        super(CardListWidget, self).__init__()
        
        self.children = []  # Initialize the list to keep track of card widgets
        
        # Scroll Area Setup
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaFrame = QFrame()  # Frame that will hold the layout of cards
        
        # Container Widget and Layout
        self.containerLayout = QVBoxLayout()
        self.containerLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scrollAreaFrame.setLayout(self.containerLayout)
        
        # Adding the frame to the scroll area
        self.scrollArea.setWidget(self.scrollAreaFrame)
        
        # Main Layout for this widget
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.scrollArea)
        self.setLayout(self.mainLayout)
        
        # Style adjustments
        self.applyStyles()

    def addCardList(self, cardList):
        """Add a list of CardViewWidgets to the list."""
        for card in cardList:
            self.addCard(card)

    def addCard(self, cardWidget):
        """Add a CardWidget to the list."""
        self.containerLayout.addWidget(cardWidget)
        self.children.append(cardWidget)  # Keep track of the card
    
    def clearAllCards(self):
        """Remove all cards from the list."""
        while len(self.children) > 0:
            card = self.children.pop()
            self.containerLayout.removeWidget(card)
            card.deleteLater()

    def clear(self):
        self.clearAllCards()

    def removeCard(self, cardWidget):
        """Remove a specific card from the list."""
        if cardWidget in self.children:
            self.children.remove(cardWidget)
            self.containerLayout.removeWidget(cardWidget)
            cardWidget.deleteLater()
    
    def applyStyles(self):
        # You can add styles specific to the card list here
        pass