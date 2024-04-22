# main.py
import sys
from PyQt5.QtWidgets import QApplication

from backend.MainModel import *
from frontend.MainWindow import *
from frontend.pages.FilesPage import *
from frontend.pages.ExamplePage import *
from frontend.pages.TracksPage import *

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # create a Data Model
    mainModel = MainModel()

    # create pages
    pages = [
        FilesPage(),
        TracksPage(),
        ExamplePage(),
    ]
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())