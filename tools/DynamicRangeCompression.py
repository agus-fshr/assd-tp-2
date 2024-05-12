import numpy as np

t = np.linspace(0, 12, 50000)

x = np.sin(2 * np.pi * t / 5)

envelope = -1*x*np.log10(t)*(1 - np.tanh(t-5)) + 0.5 + np.exp(-50*(t-10)**2)
signal = np.sin(2 * np.pi * 20 * t) * envelope



def dynamic_range_compression(input_wave, segment_size=500, threshold=1.0):
    # Calculate the number of segments
    num_segments = len(input_wave) // segment_size

    # Initialize output wave
    output_wave = np.zeros_like(input_wave)

    # Initialize the volume adjustment factors
    volume_adjustment_factors = np.ones(num_segments + 2)

    # First step: calculate the volume adjustment factors
    for i in range(num_segments):
        # Extract the current segment and the next segment
        current_segment = input_wave[i*segment_size:(i+1)*segment_size]
        next_segment = input_wave[(i+1)*segment_size:(i+2)*segment_size] if i+1 < num_segments else np.array([])

        # Calculate the maximum absolute amplitude of the current segment and the next segment
        max_amplitude_current = np.max(np.abs(current_segment))
        max_amplitude_next = np.max(np.abs(next_segment)) if next_segment.size else 0

        # If the maximum amplitude exceeds the threshold
        if max_amplitude_current > threshold or max_amplitude_next > threshold:
            # Calculate the volume adjustment factor
            volume_adjustment_factors[i+1] = threshold / max(max_amplitude_current, max_amplitude_next)

    # Second step: apply the volume adjustment factors
    for i in range(num_segments):
        # Extract the current segment
        segment = input_wave[i*segment_size:(i+1)*segment_size]

        # Calculate the volume adjustment ramp
        volume_adjustment_ramp = np.linspace(volume_adjustment_factors[i], volume_adjustment_factors[i+1], segment_size)

        # Apply the volume adjustment ramp to the segment
        output_wave[i*segment_size:(i+1)*segment_size] = segment * volume_adjustment_ramp

    # Process the remaining samples in the input wave, if any
    if len(input_wave) % segment_size != 0:
        segment = input_wave[num_segments*segment_size:]
        volume_adjustment_ramp = np.linspace(volume_adjustment_factors[-2], volume_adjustment_factors[-1], len(segment))
        output_wave[num_segments*segment_size:] = segment * volume_adjustment_ramp

    return output_wave, volume_adjustment_factors


# newSignal1 = process_mix(signal, 500)
newSignal2, volumeFactors = dynamic_range_compression(signal, segment_size=500, threshold=1.0)

volAxis = np.linspace(0, 12, len(volumeFactors))

import matplotlib.pyplot as plt
ax1 = plt

ax1.plot(t, envelope, label='Original Envelope', color='blue')
ax1.axhline(y=1, color='black', linestyle='--', lw=1.5, label='Threshold')
ax1.plot(t, newSignal2, label='New Signal', color='green', lw=0.7)
ax1.plot(volAxis, volumeFactors, label='Volume Factors', color='red', lw=0.7, marker='o', markersize=3)
ax1.grid()
ax1.legend()
plt.tight_layout()
plt.show()