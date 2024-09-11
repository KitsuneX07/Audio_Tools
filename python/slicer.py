import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Union, Iterable


def merge_short_chunks(chunks, max_duration, rate):
    merged_chunks = []
    buffer, length = [], 0

    for chunk in chunks:
        if length + len(chunk) > max_duration * rate and len(buffer) > 0:
            merged_chunks.append(np.concatenate(buffer))
            buffer, length = [chunk], 0
        else:
            buffer.append(chunk)
            length += len(chunk)

    if len(buffer) > 0:
        merged_chunks.append(np.concatenate(buffer))

    return merged_chunks


class Slicer:
    def __init__(self, sr: int, threshold: float = -40.0, min_length: int = 5000,
                 min_interval: int = 300, hop_size: int = 10, max_sil_kept: int = 5000):
        if not min_length >= min_interval >= hop_size:
            raise ValueError(
                "The following condition must be satisfied: min_length >= min_interval >= hop_size"
            )

        self.threshold = 10 ** (threshold / 20.0)
        self.hop_size = round(sr * hop_size / 1000)
        self.win_size = min(round(sr * min_interval / 1000), 4 * self.hop_size)
        self.min_length = round(sr * min_length / 1000 / self.hop_size)
        self.min_interval = round(sr * min_interval / self.hop_size)
        self.max_sil_kept = round(sr * max_sil_kept / 1000 / self.hop_size)

    def _apply_slice(self, waveform, begin, end):
        if len(waveform.shape) > 1:
            return waveform[
                   :, begin * self.hop_size: min(waveform.shape[1], end * self.hop_size)
                   ]
        else:
            return waveform[
                   begin * self.hop_size: min(waveform.shape[0], end * self.hop_size)
                   ]

    def slice(self, waveform):
        if len(waveform.shape) > 1:
            samples = waveform.mean(axis = 0)
        else:
            samples = waveform

        if samples.shape[0] <= self.min_length:
            return [waveform]

        rms_list = librosa.feature.rms(
            y = samples, frame_length = self.win_size, hop_length = self.hop_size
        ).squeeze(0)
        sil_tags = []
        silence_start = None
        clip_start = 0

        for i, rms in enumerate(rms_list):
            if rms < self.threshold:
                if silence_start is None:
                    silence_start = i
                continue

            if silence_start is None:
                continue

            is_leading_silence = silence_start == 0 and i > self.max_sil_kept
            need_slice_middle = (
                    i - silence_start >= self.min_interval
                    and i - clip_start >= self.min_length
            )

            if not is_leading_silence and not need_slice_middle:
                silence_start = None
                continue

            if i - silence_start <= self.max_sil_kept:
                pos = rms_list[silence_start: i + 1].argmin() + silence_start
                if silence_start == 0:
                    sil_tags.append((0, pos))
                else:
                    sil_tags.append((pos, pos))
                clip_start = pos
            elif i - silence_start <= self.max_sil_kept * 2:
                pos = rms_list[
                      i - self.max_sil_kept: silence_start + self.max_sil_kept + 1
                      ].argmin()
                pos += i - self.max_sil_kept
                pos_l = (
                        rms_list[
                        silence_start: silence_start + self.max_sil_kept + 1
                        ].argmin()
                        + silence_start
                )
                pos_r = (
                        rms_list[i - self.max_sil_kept: i + 1].argmin()
                        + i
                        - self.max_sil_kept
                )

                if silence_start == 0:
                    sil_tags.append((0, pos_r))
                    clip_start = pos_r
                else:
                    sil_tags.append((min(pos_l, pos), max(pos_r, pos)))
                    clip_start = max(pos_r, pos)
            else:
                pos_l = (
                        rms_list[
                        silence_start: silence_start + self.max_sil_kept + 1
                        ].argmin()
                        + silence_start
                )
                pos_r = (
                        rms_list[i - self.max_sil_kept: i + 1].argmin()
                        + i
                        - self.max_sil_kept
                )

                if silence_start == 0:
                    sil_tags.append((0, pos_r))
                else:
                    sil_tags.append((pos_l, pos_r))

                clip_start = pos_r
            silence_start = None

        total_frames = rms_list.shape[0]
        if (
                silence_start is not None
                and total_frames - silence_start >= self.min_interval
        ):
            silence_end = min(total_frames, silence_start + self.max_sil_kept)
            pos = rms_list[silence_start: silence_end + 1].argmin() + silence_start
            sil_tags.append((pos, total_frames + 1))

        if len(sil_tags) == 0:
            return [waveform]
        else:
            chunks = []

            if sil_tags[0][0] > 0:
                chunks.append(self._apply_slice(waveform, 0, sil_tags[0][0]))

            for i in range(len(sil_tags) - 1):
                chunks.append(
                    self._apply_slice(waveform, sil_tags[i][1], sil_tags[i + 1][0])
                )

            if sil_tags[-1][1] < total_frames:
                chunks.append(
                    self._apply_slice(waveform, sil_tags[-1][1], total_frames)
                )

            return chunks


def slice_by_max_duration(audio, max_duration, rate):
    max_samples = int(max_duration * rate)
    return [audio[i: i + max_samples] for i in range(0, len(audio), max_samples)]


@lru_cache(maxsize = None)
def slice_audio_file_v2(
        input_file: Union[str, Path],
        output_dir: Union[str, Path],
        min_duration: float = 180.0,
        max_duration: float = 300.0,
        min_silence_duration: float = 0.3,
        top_db: int = -40,
        hop_length: int = 10,
        max_silence_kept: float = 0.5,
        flat_layout: bool = False,
        merge_short: bool = False,
) -> None:
    output_dir = Path(output_dir)
    audio, rate = librosa.load(str(input_file), sr = None, mono = True)

    slicer = Slicer(
        sr = rate,
        threshold = top_db,
        min_length = min_duration * 1000,
        min_interval = min_silence_duration * 1000,
        hop_size = hop_length,
        max_sil_kept = max_silence_kept * 1000,
    )

    sliced_audio = slicer.slice(audio)
    if merge_short:
        sliced_audio = merge_short_chunks(sliced_audio, max_duration, rate)

    for idx, chunk in enumerate(sliced_audio):
        sliced_by_max_duration_chunk = slice_by_max_duration(chunk, max_duration, rate)
        for j, slice_chunk in enumerate(sliced_by_max_duration_chunk):
            if flat_layout:
                sf.write(str(output_dir) + f"_{idx:04d}_{j:02d}.wav", slice_chunk, rate)
            else:
                sf.write(str(output_dir / f"{idx:04d}_{j:02d}.wav"), slice_chunk, rate)


def process_folder(input_folder: Union[str, Path], output_dir: Union[str, Path], **kwargs):
    input_folder = Path(input_folder)
    wav_files = list(input_folder.glob("*.wav"))
    print(f"Found {len(wav_files)} wav files in {input_folder}")

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(slice_audio_file_v2, wav_file, output_dir, **kwargs)
            for wav_file in wav_files
        ]
        for future in futures:
            future.result()


if __name__ == "__main__":
    input_folder = ".\\gal_audio"
    output_dir = ".\\sliced"
    process_folder(input_folder, output_dir, min_duration = 180, max_duration = 300)
