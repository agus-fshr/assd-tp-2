from .handlers.MIDIHandler import *
from .handlers.FileHandler import *
from .handlers.WavHandler import *

from .synths.SynthBaseClass import *
from .synths.PhysicModelSynths import *
from .synths.AdditiveSynths import *
#from .synths.SampleSynths import *
from .synths.FMSynths import *

from .effects.EffectBaseClass import *
from .effects.Effects import *

from .utils.ParamObject import ParameterList
from .utils.AudioPlayer import AudioPlayer
from .utils.Worker import Worker

        

class MainModel:
    file_handler = FileImportHandler(name_filter="All Files (*.*);;MIDI Files (*.mid);;WAV Files (*.wav)")
    midi_handler = MIDIFilesHandler()
    wav_handler = WavHandler()
    audioPlayer = AudioPlayer()

    def __init__(self):
        self.verify()
        self.fileImportWorker = Worker(function=self.import_single_file)
        self.synthWorker = Worker(function=self.synthWorkerFunction)


    # Add synthesizers here !
    synthesizers = [
        PureToneSynth(),
        GuitarAdditive(),
        FMSynth(),
        FMSynthSax(),
        DFM_SAX(),
        DFM_OBOE(),
        DFM_FrenchHorn(),
        DFM_Harpsichord(),
        DFM_PipeOrgan(),
        DFM_Trumpet(),
        KSGuitar(),
        KSDrum(),
    ]


    # Add effects here !
    effects = [
        # NoEffect(),
        DelayEffect(),
        SimpleEchoEffect(),
        ReverbEffect(),
        FlangerEffect(),
        ReberbRIR()
    ]

    def clear_files(self):
        self.file_handler.clear()
        self.midi_handler.clear()
        self.wav_handler.clear()



    def synthWorkerFunction(self, n0, note, instrument, effect):
        midiNote = note["Note"]
        amp = note["Amplitude"]
        duration = note["Duration"]
        wave_array = instrument(midiNote, amp, duration)
        wave_array = effect(wave_array)
        return n0, wave_array
    


    def import_files(self, onFileImported):
        try:
            self.fileImportWorker.taskComplete.disconnect()
        except:
            pass
        finally:
            if onFileImported is not None:
                self.fileImportWorker.taskComplete.connect(lambda _: onFileImported())

        self.import_with_handler(self.wav_handler, "wav")
        self.import_with_handler(self.midi_handler, "mid")
        self.fileImportWorker.start()






    def import_with_handler(self, handler, ext):
        for fmeta in self.file_handler.pending_files(ext):
            self.fileImportWorker.add_task((handler, fmeta))            


    def import_single_file(self, handler, fmeta):
        if handler.import_file(fmeta.path):
            fmeta.set_ok()
            return True
        else:
            fmeta.set_error()
            return False
        

    # DO NOT TOUCH THIS FUNCTION
    def verify(self):
        synthNames = []
        effectNames = []
        for synth in self.synthesizers:
            if not isinstance(synth, SynthBaseClass):
                raise Exception(f"Synthesizer '{synth}' is not an instance of SynthBaseClass")
            if not hasattr(synth, "params") or not isinstance(synth.params, ParameterList):
                raise Exception(f"Synthesizer '{synth}' does not have a 'params' attribute of type ParameterList")
            synthNames.append(synth.name)
        for effect in self.effects:
            if not isinstance(effect, EffectBaseClass):
                raise Exception(f"Effect '{effect}' is not an instance of EffectBaseClass")
            if not hasattr(effect, "params") or not isinstance(effect.params, ParameterList):
                raise Exception(f"Effect '{effect}' does not have a 'params' attribute of type ParameterList")
            effectNames.append(effect.name)

        if len(synthNames) != len(set(synthNames)):
            raise Exception(f"Synthesizer names are not unique: {synthNames}")
        if len(effectNames) != len(set(effectNames)):
            raise Exception(f"Effect names are not unique: {effectNames}")
