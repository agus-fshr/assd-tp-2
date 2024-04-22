# mainWindow.py
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTabWidget

class MainWindow(QMainWindow):
    """ 
    Main Window class that contains a Page Navigator (tab widget)
    1) The pages should be passed as a list of QWidget objects
    2) Each page must have:
        - a title attribute
        - a method initUI(layout) that initializes the page layout
        - a model attribute that is set by the main window
    3) Each page can have:
        - a method on_tab_focus() that is called when the page is focused
        - a method on_tab_unfocus() that is called when the page is unfocused
    """ 
    def __init__(self, pages=[], model=None):
        super().__init__()
        self.last_page_index = 0
        self.model = model
        self.initUI(pages)

    def initUI(self, pages):
        self.setWindowTitle('Sintetizador MIDI')
        
        # center window on screen
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        rw, rh, sw, sh = rect.width(), rect.height(), 2*self.width(), self.height()
        self.setGeometry(rw // 2 - sw // 2, rh // 2 - sh // 2, sw, sh)

        # create tab widget (Page Navigator)
        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)
        for page in pages:
            page.set_model(self.model)
            tab_widget.addTab(page, page.title)

        # set tab change event
        tab_widget.currentChanged.connect(self.tab_changed)
        tab_widget.setStyleSheet("QWidget { background-color: #f5f5f5 }")

        self.show()


    def tab_changed(self, index):
        tab_widget = self.centralWidget()

        # unfocus last active tab
        last_widget = tab_widget.widget(self.last_page_index)
        if hasattr(last_widget, 'on_tab_unfocus'): 
            last_widget.on_tab_unfocus()

        # get newly active tab
        current_widget = tab_widget.widget(index)
        self.last_page_index = index

        # check if method exists
        if hasattr(current_widget, 'on_tab_focus'): 
            current_widget.on_tab_focus()