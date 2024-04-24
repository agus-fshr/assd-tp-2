import wave
import io
import numpy as np

def np_array_to_wave(np_array, framerate=44100, channels=1):
    # Ensure the numpy array is of type int16
    np_array = np_array.astype(np.int16)
    
    # Convert the numpy array to bytes
    byte_data = np_array.tobytes()
    
    # Create a new wave file in memory
    wave_obj = io.BytesIO()
    with wave.open(wave_obj, 'wb') as wo:
        wo.setnchannels(channels)
        wo.setsampwidth(2)  # 2 bytes for np.int16
        wo.setframerate(framerate)
        wo.writeframes(byte_data)
    
    # Reset the buffer's file position to the beginning
    wave_obj.seek(0)
    
    # Return the wave object
    return wave.open(wave_obj, 'rb')