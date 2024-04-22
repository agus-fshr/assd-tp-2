# main.py
import sys
from PyQt5.QtWidgets import QApplication

from backend.MainModel import *
from frontend.MainWindow import *
from frontend.pages.FilesPage import *
from frontend.pages.ExamplePage import *

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create a Data Model
    mainModel = MainModel()

    # create pages
    pages = [
        FilesPage(),
        ExamplePage()
    ]
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())