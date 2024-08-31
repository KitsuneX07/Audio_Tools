"""
将分离的opencpop音频文件合并。
"""

import os
from pydub import AudioSegment

def merge(opencpop_folder_path, output_folder_path):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    file_dict = {}

    for file in os.listdir(opencpop_folder_path):
        if file.endswith(".wav"):
            key = file[:4]
            if key not in file_dict:
                file_dict[key] = []
            file_dict[key].append(file)

    for key, files in file_dict.items():
        files.sort()
        combined = AudioSegment.empty()
        silent_segment = AudioSegment.silent(duration=1000)  # 1秒的静音段

        for file in files:
            file_path = os.path.join(opencpop_folder_path, file)
            audio_segment = AudioSegment.from_wav(file_path)
            if combined:
                combined += silent_segment  # 在每个音频片段之间添加1s静音
            combined += audio_segment

        # 输出合并后的音频
        output_path = os.path.join(output_folder_path, f'{key}_merged.wav')
        combined.export(output_path, format="wav")
        print(f'Merged {len(files)} files into {output_path}')

if __name__ == '__main__':
    opencpop_folder_path = "D:\\download\\BaiduNetdiskDownload\\opencpop"
    output_folder_path = ".\\opencpop_merged"
    merge(opencpop_folder_path, output_folder_path)