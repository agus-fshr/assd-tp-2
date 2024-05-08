# main.py
import sys
from PyQt5.QtWidgets import QApplication

print("Running main.py")

from frontend.MainWindow import *
# from frontend.pages.TestPage import *
from frontend.pages.FilesPage import *
from frontend.pages.ChordPage import *
from frontend.pages.TracksPage import *
from frontend.pages.MidiViewer import *
from frontend.pages.TrackPlayer import *
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
        TracksMetadataPage(),
        MidiViewer(),
        
        InstrumentPage(),
        ChordPage(),
        SoundPlayerPage(),
        TrackPlayer(),
        # TestPage(),
        # ReadMidiPage(),
    ]
    print("Pages created, creating main window")
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())