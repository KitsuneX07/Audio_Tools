import os
import subprocess


def get_all_ogg_files(dir_path):
    ogg_files = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.ogg'):
                ogg_files.append(os.path.join(root, file))
    return ogg_files


def get_audio_sample_rate(file_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate',
         '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT
    ).stdout.decode().strip()

    return int(result)


def create_silence(sample_rate = 48000, duration = 1, filename = 'silence.ogg'):
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', f'-i', f'anullsrc=r={sample_rate}:cl=stereo',
        '-t', str(duration), '-q:a', '9', filename
    ])


def generate_filelist(file_list, silence_file, log_file):
    with open('filelist.txt', 'w') as f:
        for i, filepath in enumerate(file_list):
            f.write(f"file '{filepath}'\n")
            if i < len(file_list) - 1:
                f.write(f"file '{silence_file}'\n")

    # Update the log file with completed batch
    with open(log_file, 'a') as log:
        for filepath in file_list:
            log.write(f"{filepath}\n")


def load_processed_files(log_file):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, 'r') as log:
        return set(line.strip() for line in log)


def merge_files(output_filename):
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', output_filename])


def merge_ogg_in_batches(input_dir, output_dir, start_index = 1, batch_size = 1000):
    ogg_files = get_all_ogg_files(input_dir)
    if not ogg_files:
        print("No OGG files found.")
        return

    os.makedirs(output_dir, exist_ok = True)

    sample_rate = get_audio_sample_rate(ogg_files[0])
    silence_file = 'silence.ogg'
    create_silence(sample_rate, 1, silence_file)

    log_file = 'processed.log'
    processed_files = load_processed_files(log_file)
    index = start_index

    for i in range(0, len(ogg_files), batch_size):
        batch_files = ogg_files[i:i + batch_size]
        filtered_batch_files = [f for f in batch_files if f not in processed_files]
        if not filtered_batch_files:
            index += 1
            continue

        generate_filelist(filtered_batch_files, silence_file, log_file)

        output_filename = os.path.join(output_dir, f"audio_{index}.ogg")
        merge_files(output_filename)

        print(f"Generated: {output_filename}")
        index += 1

    os.remove(silence_file)


if __name__ == "__main__":
    input_directory = r"D:\projects\python\Audio_Tools\python\raw"
    output_directory = r"D:\projects\python\Audio_Tools\python\gal_audio"
    start_index = 1
    merge_ogg_in_batches(input_directory, output_directory, start_index, batch_size = 50)
