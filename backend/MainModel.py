from .handlers.MIDIHandler import *
from .handlers.FileHandler import *
from .handlers.WavHandler import *

from .synths.SynthBaseClass import *
from .effects.EffectBaseClass import *
from .ParamObject import ParameterList

from .synths.PhysicModelSynths import *
from .synths.AdditiveSynths import *
from .synths.SampleSynths import *
from .synths.FMSynths import *

from .effects.Effects import *

from .audio.AudioPlayer import AudioPlayer

class MainModel:
    def __init__(self):
        self.verify()

    file_handler = FileImportHandler(name_filter="All Files (*.*);;MIDI Files (*.mid);;WAV Files (*.wav)")
    midi_handler = MIDIFilesHandler()
    wav_handler = WavHandler()
    audioPlayer = AudioPlayer()


    # Add synthesizers here !
    synthesizers = [
        PureToneSynth(),
        GuitarAdditive(),
        FMSynth(),
        KSGuitar(),
    ]

    # Add effects here !
    effects = [
        # NoEffect(),
        DelayEffect(),
        SimpleEchoEffect(),
        FlangerEffect(),
        ReberbRIR()
    ]


    def clear_files(self):
        self.file_handler.clear()
        self.midi_handler.clear()
        self.wav_handler.clear()


    def import_files(self):
        self.import_with_handler(self.wav_handler, "wav")
        self.import_with_handler(self.midi_handler, "mid")


    def import_with_handler(self, handler, ext):
        for fmeta in self.file_handler.pending_files(ext):
            if handler.import_file(fmeta.path):
                fmeta.set_ok()
            else:
                fmeta.set_error()


    # DO NOT TOUCH THIS FUNCTION
    def verify(self):
        for synth in self.synthesizers:
            if not isinstance(synth, SynthBaseClass):
                raise Exception(f"Synthesizer '{synth}' is not an instance of SynthBaseClass")
            if not hasattr(synth, "params") or not isinstance(synth.params, ParameterList):
                raise Exception(f"Synthesizer '{synth}' does not have a 'params' attribute of type ParameterList")
        for effect in self.effects:
            if not isinstance(effect, EffectBaseClass):
                raise Exception(f"Effect '{effect}' is not an instance of EffectBaseClass")
            if not hasattr(effect, "params") or not isinstance(effect.params, ParameterList):
                raise Exception(f"Effect '{effect}' does not have a 'params' attribute of type ParameterList")
