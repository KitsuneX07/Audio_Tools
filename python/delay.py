"""
用于给音频添加delay效果，制作MSST数据集。
"""

import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter
import os


# 滤波器
def butter_filter(data, cutoff, fs, filter_type="low", order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    return lfilter(b, a, data)


# 模拟调制
def apply_modulation(audio, sr, depth, rate):
    modulated_audio = np.copy(audio)
    samples = np.arange(len(audio))
    modulation = depth * np.sin(2 * np.pi * rate * samples / sr)
    modulated_audio *= 1 + modulation
    return modulated_audio


def delay_audio(input_audio_path, index, output_path):
    # 参数设置
    max_delay_time = np.clip(np.random.normal(0.15, 0.05), 0.05, 2.50)
    mod_rate = np.clip(np.random.normal(0.15, 0.05), 0.05, 0.25)
    feedback = np.clip(np.random.normal(0.5, 0.1), 0.2, 0.7)
    mix = np.clip(np.random.normal(0.5, 0.1), 0.2, 0.8)
    highpass_cutoff = np.clip(np.random.normal(150.0, 50.0), 50.0, 300.0)
    lowpass_cutoff = np.clip(np.random.normal(5000.0, 700.0), 3000.0, 7000.0)
    mod_depth = np.clip(np.random.normal(0.1, 0.05), 0.01, 0.2)
    mod_rate_freq = np.clip(np.random.normal(0.3, 0.1), 0.1, 0.5)

    use_filters = np.random.binomial(1, 0.5) == 1  # 使用二项分布随机选择应用滤波器
    use_modulation = np.random.binomial(1, 0.5) == 1

    input_audio, sr = librosa.load(input_audio_path, sr=None)

    max_delay_samples = int(max_delay_time * sr)
    output_audio = np.zeros(len(input_audio) + max_delay_samples)
    delay_audio = np.zeros_like(output_audio)

    delay_modulation = (np.sin(np.linspace(0, mod_rate * 2 * np.pi, len(input_audio))) + 1) / 2
    delay_modulation *= max_delay_samples

    for i in range(len(input_audio)):
        current_delay_samples = int(delay_modulation[i])

        if i >= current_delay_samples:
            delayed_feedback = feedback * output_audio[i - current_delay_samples]
            delay_audio[i + current_delay_samples] += input_audio[i] * mix + delayed_feedback
            output_audio[i] += delayed_feedback

    delay_only_audio = delay_audio[: len(input_audio)]

    if use_filters:
        delay_only_audio = butter_filter(delay_only_audio, highpass_cutoff, sr, filter_type="high")
        delay_only_audio = butter_filter(delay_only_audio, lowpass_cutoff, sr, filter_type="low")

    if use_modulation:
        delay_only_audio = apply_modulation(delay_only_audio, sr, mod_depth, mod_rate_freq)

    mixed_audio = input_audio + delay_only_audio * mix

    output_dir = os.path.join(output_path, f"song_{index}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sf.write(os.path.join(output_dir, "noreverb.wav"), input_audio, sr)
    sf.write(os.path.join(output_dir, "reverb.wav"), delay_only_audio, sr)
    sf.write(os.path.join(output_dir, "mixture.wav"), mixed_audio, sr)


def process_folder(input_folder):
    print("Processing folder", input_folder)
    file_paths = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file == "vocals.wav":  # 处理MUSDB18数据集
                # if file.endswith('.wav'):
                file_paths.append(os.path.join(root, file))
    print("Found", len(file_paths), "files")
    return file_paths


if __name__ == "__main__":
    input_folder_path = "D:\\download\\idm\\musdb18hq\\test"
    output_path = ".\\dataset"
    index = 200
    for _, file_path in enumerate(process_folder(input_folder_path)):
        print("Processing ", index, file_path)
        delay_audio(file_path, index, output_path)
        index += 1
