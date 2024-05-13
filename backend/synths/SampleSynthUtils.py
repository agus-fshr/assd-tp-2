"""
Utilities for the Sample Synthesizer

References:
[1] https://github.com/sannawag/TD-PSOLA/
[2] https://speechprocessingbook.aalto.fi/Representations/Pitch-Synchoronous_Overlap-Add_PSOLA.html
"""

import numpy as np
from numpy.fft import fft, ifft

def shift_pitch(signal, fs, f_ratio):
    """
    Calls PSOLA pitch shifting algorithm
    :param signal: original signal in the time-domain
    :param fs: sample_rate
    :param f_ratio: ratio by which the frequency will be shifted
    :return: pitch-shifted signal
    """

    peaks = find_peaks(signal, fs)
    new_signal = psola(signal, peaks, f_ratio)
    return new_signal

def find_peaks(signal, fs, max_hz=950, min_hz=75, analysis_win_ms=40, max_change=1.005, min_change=0.995):
    """
    Find sample indices of peaks in time-domain signal
    :param max_hz: maximum measured fundamental frequency
    :param min_hz: minimum measured fundamental frequency
    :param analysis_win_ms: window size used for autocorrelation analysis
    :param max_change: restrict periodicity to not increase by more than this ratio from the mean
    :param min_change: restrict periodicity to not decrease by more than this ratio from the mean
    :return: peak indices
    """
    N = len(signal)
    min_period = fs // max_hz
    max_period = fs // min_hz

    # compute pitch periodicity
    sequence = int(analysis_win_ms / 1000 * fs)  # analysis sequence length in samples
    periods = compute_periods_per_sequence(signal, sequence, min_period, max_period)

    # simple hack to avoid octave error: assume that the pitch should not vary much, restrict range
    mean_period = np.mean(periods)
    max_period = int(mean_period * 1.1)
    min_period = int(mean_period * 0.9)
    periods = compute_periods_per_sequence(signal, sequence, min_period, max_period)

    # find the peaks
    peaks = [np.argmax(signal[:int(periods[0]*1.1)])]
    while True:
        prev = peaks[-1]
        idx = prev // sequence  # current autocorrelation analysis window
        if prev + int(periods[idx] * max_change) >= N:
            break
        # find maximum near expected location
        peaks.append(prev + int(periods[idx] * min_change) +
                np.argmax(signal[prev + int(periods[idx] * min_change): prev + int(periods[idx] * max_change)]))
    return np.array(peaks)

def compute_periods_per_sequence(signal, sequence, min_period, max_period):
    """
    Computes periodicity of a time-domain signal using autocorrelation
    :param sequence: analysis window length in samples. Computes one periodicity value per window
    :param min_period: smallest allowed periodicity
    :param max_period: largest allowed periodicity
    :return: list of measured periods in windows across the signal
    """
    N = len(signal)
    offset = 0  # current sample offset
    periods = []  # period length of each analysis sequence

    while offset < N:
        fourier = fft(signal[offset: offset + sequence])
        fourier[0] = 0  # remove DC component
        autoc = ifft(fourier * np.conj(fourier)).real
        autoc_peak = min_period + np.argmax(autoc[min_period: max_period])
        periods.append(autoc_peak)
        offset += sequence
    return periods


def psola(signal, peaks, f_ratio):
    """
    Time-Domain Pitch Synchronous Overlap and Add
    :param signal: original time-domain signal
    :param peaks: time-domain signal peak indices
    :param f_ratio: pitch shift ratio
    :return: pitch-shifted signal
    """
    N = len(signal)
    # Interpolate
    new_signal = np.zeros(N)
    new_peaks_ref = np.linspace(0, len(peaks) - 1, len(peaks) * f_ratio)
    new_peaks = np.zeros(len(new_peaks_ref)).astype(int)

    for i in range(len(new_peaks)):
        weight = new_peaks_ref[i] % 1
        left = np.floor(new_peaks_ref[i]).astype(int)
        right = np.ceil(new_peaks_ref[i]).astype(int)
        new_peaks[i] = int(peaks[left] * (1 - weight) + peaks[right] * weight)

    # PSOLA
    for j in range(len(new_peaks)):
        # find the corresponding old peak index
        i = np.argmin(np.abs(peaks - new_peaks[j]))
        # get the distances to adjacent peaks
        P1 = [new_peaks[j] if j == 0 else new_peaks[j] - new_peaks[j-1],
              N - 1 - new_peaks[j] if j == len(new_peaks) - 1 else new_peaks[j+1] - new_peaks[j]]
        # edge case truncation
        if peaks[i] - P1[0] < 0:
            P1[0] = peaks[i]
        if peaks[i] + P1[1] > N - 1:
            P1[1] = N - 1 - peaks[i]
        # linear OLA window
        window = list(np.linspace(0, 1, P1[0] + 1)[1:]) + list(np.linspace(1, 0, P1[1] + 1)[1:])
        # center window from original signal at the new peak
        new_signal[new_peaks[j] - P1[0]: new_peaks[j] + P1[1]] += window * signal[peaks[i] - P1[0]: peaks[i] + P1[1]]
    return new_signal
