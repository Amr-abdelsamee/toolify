import librosa
import numpy as np
from tqdm import tqdm


def get_silent_parts(input_file_path, silence_threshold_db=-40, silence_margin_sec=0.15):
    y, sr = librosa.load(input_file_path)

    db = librosa.amplitude_to_db(np.abs(y))
    margin_samples = int(sr * silence_margin_sec)

    non_silent = db > silence_threshold_db

    silent_parts = []
    is_silent = False
    start_idx = 0

    for i in tqdm(range(len(non_silent))):
        if non_silent[i] and is_silent:
            end_idx = i
            start_idx += margin_samples
            end_idx -= margin_samples

            start_time = start_idx / sr
            end_time = end_idx / sr
            duration = end_time - start_time
            duration += silence_margin_sec * 2
            silent_parts.append(
                {
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                    "start_sec": start_time,
                    "end_sec": end_time,
                    "duration": duration,
                }
            )
            is_silent = False
        elif not non_silent[i] and not is_silent:
            # Start of silent region
            start_idx = i
            is_silent = True

    # if the audio ends with silence
    if is_silent:
        # end_inc is added to avoid trimming the pause at the end of the sentence
        end_inc = 1.25
        margin_samples = int(margin_samples * end_inc)
        end_idx = len(y)
        start_idx += margin_samples

        start_time = start_idx / sr
        end_time = end_idx / sr
        duration = end_time - start_time
        duration += silence_margin_sec * end_inc
        silent_parts.append(
            {
                "start_idx": start_idx,
                "end_idx": end_idx,
                "start_sec": start_time,
                "end_sec": end_time,
                "duration": duration,
            }
        )
    return silent_parts, y, sr
