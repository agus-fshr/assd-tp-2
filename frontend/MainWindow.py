# mainWindow.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon
from frontend.pages.BaseClassPage import BaseClassPage

# DO NOT TOUCH THIS CODE
class MainWindow(QMainWindow):
    """ 
    Main Window class that contains a Page Navigator (tab widget)
    1) The pages object instances should be derived from BaseClassPage and passed as a list
    2) Each page must have:
        - a .title (str) attribute
        - a method initUI(layout) that initializes the page layout (layout is a QVBoxLayout object)
        - a model attribute that is set by the main window
    3) Each page can have:
        - a method on_tab_focus() that is called when the page is focused
        - a method on_tab_unfocus() that is called when the page is unfocused
    """ 
    def __init__(self, pages, model):
        super().__init__()
        self.last_page_index = 0
        self.model = model
        self.initUI(pages)

    def initUI(self, pages):
        self.setWindowTitle('Sintetizador MIDI')
        self.setWindowIcon(QIcon('frontend/assets/icon.png'))
        
        # center window on screen
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        rw, rh, sw, sh = rect.width(), rect.height(), 2*self.width(), int(1.5*self.height())
        self.setGeometry(rw // 2 - sw // 2, rh // 2 - sh // 2, sw, sh)

        # Check we don't have repeated titles
        titles = [page.title for page in pages]
        if len(titles) != len(set(titles)):
            raise Exception("All pages must have unique titles")

        # create tab widget (Page Navigator) and add pages
        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)
        for page in pages:
            # Check if page is a BaseClassPage object
            if not isinstance(page, BaseClassPage):
                raise Exception("All pages must be subclasses of BaseClassPage")
            page.set_model(self.model)
            page.initUI(page.layout)
            page.setLayout(page.layout)
            tab_widget.addTab(page, page.title)

        # set tab change event
        tab_widget.currentChanged.connect(self.tab_changed)
        tab_widget.setStyleSheet("QWidget { background-color: #f5f5f5 }")

        self.show()


    def tab_changed(self, index):
        tab_widget = self.centralWidget()

        # unfocus last active tab
        last_page = tab_widget.widget(self.last_page_index)
        if hasattr(last_page, 'on_tab_unfocus'): 
            print(f"Page {self.last_page_index} '{last_page.title}' unfocused")
            last_page.on_tab_unfocus()

        # get newly active tab
        current_page = tab_widget.widget(index)
        self.last_page_index = index

        # check if method exists
        if hasattr(current_page, 'on_tab_focus'): 
            print(f"Page {index} '{current_page.title}' focused")
            current_page.on_tab_focus()