import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve
import os


def read_wav(file_path):
    """Read a wav file and return its sample rate and data."""
    sample_rate, data = wavfile.read(file_path)
    return sample_rate, data.astype(np.float32)


def write_wav(file_path, sample_rate, data):
    """Write data to a wav file."""
    max_int16 = 32767
    data = np.clip(data, -max_int16, max_int16)
    wavfile.write(file_path, sample_rate, data.astype(np.int16))


def normalize_audio(audio):
    """Normalize audio to prevent clipping."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        print(f"Normalization factor: {max_val}")  # Debug information
        return audio / max_val
    return audio


def convolve_audio(signal, ir):
    """Perform the convolution of the raw audio with the impulse response (IR)."""
    return fftconvolve(signal, ir, mode = 'full')


def process_audio_in_chunks(audio, ir, chunk_size):
    """Process audio in chunks to avoid memory issues."""
    num_chunks = int(np.ceil(len(audio) / chunk_size))
    reverb_data_left = np.zeros(len(audio) + len(ir) - 1)
    reverb_data_right = np.zeros(len(audio) + len(ir) - 1)

    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(audio))

        print(f"Processing chunk {i + 1}/{num_chunks} (samples {start} to {end})")

        chunk_left = audio[start:end, 0]
        chunk_right = audio[start:end, 1]

        reverb_chunk_left = convolve_audio(chunk_left, ir[:, 0])
        reverb_chunk_right = convolve_audio(chunk_right, ir[:, 1])

        reverb_data_left[start:start + len(reverb_chunk_left)] += reverb_chunk_left
        reverb_data_right[start:start + len(reverb_chunk_right)] += reverb_chunk_right

    return np.stack((reverb_data_left, reverb_data_right), axis = -1)


def main():
    # Specify the paths to the input audio files
    noreverb_path = r"D:\projects\python\Audio_Tools\python\gal_audio\audio_147.wav"
    ir_path = r"D:\projects\python\Audio_Tools\python\data\IR\01 Hall 1.wav"

    # Read the original and IR audio files
    sample_rate, noreverb_data = read_wav(noreverb_path)
    _, ir_data = read_wav(ir_path)

    # Debug: Print shapes of the input audio data
    print(f"Original audio shape: {noreverb_data.shape}")
    print(f"IR audio shape: {ir_data.shape}")

    # Normalize IR to prevent clipping
    ir_data = normalize_audio(ir_data)

    # Define chunk size
    chunk_size = 44100 * 10  # 10 seconds

    # Process the audio in chunks
    reverb_data = process_audio_in_chunks(noreverb_data, ir_data, chunk_size)

    # Trim the reverb data to the length of the original audio
    reverb_data = reverb_data[:len(noreverb_data)]

    # Normalize the reverb data
    reverb_data = normalize_audio(reverb_data)

    # Debug: Write reverb data before any further processing
    write_wav(os.path.join(os.getcwd(), 'reverb_test.wav'), sample_rate, reverb_data)

    # Create the mixture audio by adding the original and reverb audio
    mixture_data = noreverb_data + reverb_data

    # Ensure the mixture is normalized to prevent clipping
    mixture_data = normalize_audio(mixture_data)

    # Write the outputs to wav files in the root directory
    write_wav(os.path.join(os.getcwd(), 'noreverb_output.wav'), sample_rate, noreverb_data)
    write_wav(os.path.join(os.getcwd(), 'reverb.wav'), sample_rate, reverb_data)
    write_wav(os.path.join(os.getcwd(), 'mixture.wav'), sample_rate, mixture_data)


if __name__ == '__main__':
    main()
