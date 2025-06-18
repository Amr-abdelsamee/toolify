import librosa
import numpy as np
from tqdm import tqdm
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt


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


def get_spectrogram(file, save_path=None, fft_size=2048, hop_size=None, window_size=None, xticks=None, yticks=None, fig_size=(10, 4), show_save=(False, True), save_params=None):
    """
    spectrogram is a visual representation of the spectrum of frequencies of a signal as it varies with time.
    """
    signal, sample_rate = sf.read(file)

    # default values taken from the librosa documentation
    if not window_size:
        window_size = fft_size

    if not hop_size:
        hop_size = window_size // 4

    stft = librosa.stft(
        signal,
        n_fft=fft_size,
        hop_length=hop_size,
        win_length=window_size,
        center=False,
    )
    spectrogram = np.abs(stft)
    spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)

    plt.figure(figsize=fig_size)
    img = librosa.display.specshow(
        spectrogram_db,
        y_axis="log",
        x_axis="time",
        sr=sample_rate,
        hop_length=hop_size,
        cmap="inferno",
    )
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    if xticks:
        plt.yticks(xticks)
    if yticks:        
        plt.yticks(yticks)

    plt.colorbar(img, format="%+2.f dBFS")

    SAVE_PARAMS = {"dpi": 300, "bbox_inches": "tight", "transparent": True}
    if show_save[1]:
        if not save_params:
            save_params = SAVE_PARAMS
        if not save_path:
            save_path = file.replace(".wav", ".png")
        plt.savefig(save_path,**save_params)
    if show_save[0]:
        plt.show()
    plt.close()
