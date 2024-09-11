import os
import subprocess


def convert_ogg_to_wav(input_folder, target_sr = 44100):
    for filename in os.listdir(input_folder):
        if filename.endswith('.ogg'):
            file_path = os.path.join(input_folder, filename)
            output_file = os.path.join(input_folder, filename.replace('.ogg', '.wav'))

            # 使用 ffmpeg 进行转换
            command = [
                'ffmpeg', '-i', file_path,
                '-ar', str(target_sr),
                '-ac', '2',  # 设置为双声道
                '-acodec', 'pcm_s16le',
                output_file
            ]
            subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)


if __name__ == "__main__":
    input_folder = r"D:\projects\python\Audio_Tools\python\gal_audio"
    convert_ogg_to_wav(input_folder)
