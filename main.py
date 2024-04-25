# main.py
import sys
from PyQt5.QtWidgets import QApplication

from frontend.MainWindow import *
from frontend.pages.FilesPage import *
from frontend.pages.TracksPage import *
from frontend.pages.ExamplePage import *
from frontend.pages.InstrumentPage import *
from frontend.pages.SoundPlayerPage import *
from frontend.pages.TracksMetadataPage import *
    
from backend.MainModel import *
from backend.synths.SynthBaseClass import *
from backend.effects.EffectBaseClass import *
from backend.ParamObject import ParameterList

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # create a Data Model
    mainModel = MainModel()

    for synth in mainModel.synthesizers:
        if not isinstance(synth, SynthBaseClass):
            raise Exception(f"Synthesizer '{synth}' is not an instance of SynthBaseClass")
        if not hasattr(synth, "params") or not isinstance(synth.params, ParameterList):
            raise Exception(f"Synthesizer '{synth}' does not have a 'params' attribute of type ParameterList")
    for effect in mainModel.effects:
        if not isinstance(effect, EffectBaseClass):
            raise Exception(f"Effect '{effect}' is not an instance of EffectBaseClass")
        if not hasattr(effect, "params") or not isinstance(effect.params, ParameterList):
            raise Exception(f"Effect '{effect}' does not have a 'params' attribute of type ParameterList")

    # create pages
    pages = [
        FilesPage(),
        TracksPage(),
        InstrumentPage(),
        SoundPlayerPage(),
        TracksMetadataPage(),
        ExamplePage(),
    ]
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())