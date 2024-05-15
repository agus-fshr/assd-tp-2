# CardWidget, CardListWidget

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QStyle, QHBoxLayout, QToolButton, QScrollArea, QFrame
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt


class CardWidget(QWidget):
    def __init__(self, child=None, icon=QStyle.SP_DriveCDIcon, title="Card", subtitle="subt", width=None, height=None, iconSize=64):
        super(CardWidget, self).__init__()
        
        # Container widget
        self.container = QWidget()
        self.containerLayout = QHBoxLayout()
        self.containerLayout.setContentsMargins(10, 10, 10, 10)
        self.containerLayout.setSpacing(10)
        self.container.setLayout(self.containerLayout)

        
        # Set up the shadow effect for the container widget
        self.shadowEffect = QGraphicsDropShadowEffect()
        self.shadowEffect.setBlurRadius(15)
        self.shadowEffect.setColor(QColor(0, 0, 0, 80))
        self.shadowEffect.setXOffset(0)
        self.shadowEffect.setYOffset(4)
        self.container.setGraphicsEffect(self.shadowEffect)
        
        # Use a standard icon
        iconLabel = QLabel()
        icon = self.style().standardIcon(icon)
        pixmap = icon.pixmap(iconSize, iconSize)
        iconLabel.setPixmap(pixmap)
        iconLabel.setAlignment(Qt.AlignCenter)
        iconLayout = QHBoxLayout()
        iconLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        iconLayout.addWidget(iconLabel)
        
        # Main Title
        titleLabel = QLabel(title)
        titleLabel.setFont(QFont('Arial', 16, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignLeft)
        subtitleLabel = QLabel(subtitle)
        
        # Add a vertical layout for the contents (Title and Child widget)
        titlesLayout = QVBoxLayout()
        titlesLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Add widgets to container layout
        titlesLayout.addWidget(titleLabel)
        titlesLayout.addWidget(subtitleLabel)
        titlesLayout.addLayout(iconLayout)

        self.containerLayout.addLayout(titlesLayout)
        if child is not None:
            if isinstance(child, QWidget):
                self.containerLayout.addWidget(child)
            elif isinstance(child, list):
                for c in child:
                    if isinstance(c, QWidget):
                        self.containerLayout.addWidget(c)
                    elif isinstance(c, QHBoxLayout) or isinstance(c, QVBoxLayout):
                        self.containerLayout.addLayout(c)
                    else:
                        raise Exception("Child must be a QWidget or a list of QWidget")
            elif isinstance(child, QHBoxLayout) or isinstance(child, QVBoxLayout):
                self.containerLayout.addLayout(child)
            else:
                raise Exception("Child must be a QWidget, a list of QWidget, or a QHBoxLayout/VBoxLayout")
        
        # Main layout for the widget
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.container)
        self.setLayout(self.mainLayout)
        
        # Apply styles to ensure visual unity
        self.applyStyles()

        # Set fixed size for the whole widget
        if width is not None and height is not None:
            self.setFixedSize(width, height)  # Example fixed size
        elif width is not None:
            self.setFixedWidth(width)
        elif height is not None:
            self.setFixedHeight(height)

    def applyStyles(self):
        self.container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 10px;
            }
        """)
        self.setStyleSheet("""
            QLabel, QPushButton {
                color: #333;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                margin-top: 5px;
            }
        """)






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
        wrapperLayout = QVBoxLayout()
        wrapperLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wrapperLayout.addLayout(self.containerLayout)
        wrapperLayout.addStretch(1)
        self.scrollAreaFrame.setLayout(wrapperLayout)
        
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

    def __iter__(self):
        return iter(self.children)

    def addCard(self, cardWidget):
        """Add a CardWidget to the list."""
        self.containerLayout.addWidget(cardWidget)
        self.children.append(cardWidget)  # Keep track of the card
    
    def clearAllCards(self):
        """Remove all cards from the list."""
        while self.children:
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

    def popCard(self):
        """Remove the last card from the list."""
        if self.children:
            card = self.children.pop()
            self.containerLayout.removeWidget(card)
            card.deleteLater()
    
    def applyStyles(self):
        # You can add styles specific to the card list here
        pass