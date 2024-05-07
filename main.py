# main.py
import sys
from PyQt5.QtWidgets import QApplication

from frontend.MainWindow import *
from frontend.pages.TestPage import *
from frontend.pages.FilesPage import *
from frontend.pages.TracksPage import *
from frontend.pages.ExamplePage import *
from frontend.pages.ReadMidiPage import *
from frontend.pages.InstrumentPage import *
from frontend.pages.SoundPlayerPage import *
from frontend.pages.TracksMetadataPage import *
    
from backend.MainModel import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # create a Data Model
    mainModel = MainModel()

    # create pages
    pages = [
        FilesPage(),
        TracksPage(),
        InstrumentPage(),
        SoundPlayerPage(),
        TracksMetadataPage(),
        ExamplePage(),
        TestPage(),
        ReadMidiPage(),
    ]
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())