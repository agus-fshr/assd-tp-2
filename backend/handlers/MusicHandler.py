import numpy as np

class MusicNote():
    freq = 0
    amp = 0
    duration = 0
    delay = 0

class MusicHandler():
    def __init__(self):
        self.noteArr = []
        self.volume = 1.0
        self.time_limits = [0, 1e9]
        self.framerate = 44100
        self.total_time = 0
        self.extra_time = 2.0

        self.buffer = None
        self.buffer_size = 0


    def clear(self):
        self.noteArr = []
        self.total_time = 0

    def set_volume(self, volume):
        self.volume = volume

    def reserve_buffer(self):
        if self.total_time == 0:
            self.calculate_total_time()
        self.buffer_size = int((self.total_time + self.extra_time) * self.framerate)
        self.buffer = np.zeros(self.buffer_size)

    def effectWorkerFunction(self, wave, effect):
        if self.buffer is None:
            self.reserve_buffer()
        if not callable(effect):
            raise Exception("Effect must be a callable function")
        out = effect(wave)
        return out

    def synthWorkerFunction(self, note, instrument):
        if self.buffer is None:
            self.reserve_buffer()
        if not isinstance(note, MusicNote):
            raise Exception("Note must be a MusicNote object")
        f = note.freq
        a = note.amp
        d = note.duration
        out = instrument(f, a, d)


    def insert_wave(self, t0, wave):
        n0 = int(t0 * self.framerate)
        n1 = n0 + wave.size
        if n0 < 0 or n0 >= self.buffer_size:
            raise Exception("Waveform start time out of bounds")
        if n1 > self.buffer_size:
            n1 = self.buffer_size
            wave = wave[:n1 - n0]
            raise ValueError("Waveform too long, truncating")
        try:
            self.buffer[n0:n1] += wave
        except ValueError as e:
            print(e)
            print(f"n0: {n0}, n1: {n1}, buffer_size: {self.buffer_size}, wave_size: {wave.size}")
        except Exception as e:
            print(e)
            print(f"n0: {n0}, n1: {n1}, buffer_size: {self.buffer_size}, wave_size: {wave.size}")



    def set_time_limits(self, start=0.0, end=1e9):
        if start > end:
            raise Exception("Start time must be less than end time")
        self.time_limits = [start, end]


    def add_note(self, freq, amp, duration, delay):
        note = MusicNote()
        note.freq = freq
        note.amp = amp
        note.duration = duration
        note.delay = delay

        self.noteArr.append(note)


    def pop_note(self):
        note = self.noteArr.pop()
        self.calculate_total_time()
        return note


    def add_midi_notes(self, midi_notes):
        lastTime = 0.0
        if not isinstance(midi_notes, list):
            midi_notes = [midi_notes]

        total_delay = 0
        initial_time = self.total_time
        for mn in midi_notes:
            if mn.time_on < self.time_limits[0]:
                lastTime = mn.time_on
                continue
            if mn.time_off >= self.time_limits[1]:
                print(f"time_off >= {self.time_limits[1]}s, breaking loop.")
                break
            if self.total_time >= (self.time_limits[1] - self.time_limits[0]):
                print(f"Total time >= {self.time_limits[1] - self.time_limits[0]}s, breaking loop.")
                break

            note = MusicNote()
            delay = mn.time_on - lastTime
            lastTime = mn.time_on

            note.freq = self.midi_to_freq(mn.note)
            note.amp = (mn.velocity / 127) * self.volume
            note.duration = mn.duration
            note.delay = delay

            self.noteArr.append(note)
            total_delay += delay
            self.total_time = max(self.total_time, total_delay + note.duration  + initial_time)



    def calculate_total_time(self):
        self.total_time = 0
        delay = 0
        for note in self.noteArr:
            delay += note.delay
            self.total_time = max(self.total_time, delay + note.duration)
    
    
    @staticmethod
    def midi_to_freq(midi):
        return 440 * 2**((midi - 69) / 12)