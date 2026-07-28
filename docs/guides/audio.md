# Audio

## Detect silent regions

```python
from toolify.audio import get_silent_parts

silent_parts, waveform, sample_rate = get_silent_parts(
    "recording.wav",
    silence_threshold_db=-40,
    silence_margin_sec=0.15,
)

for part in silent_parts:
    print(part["start_sec"], part["end_sec"], part["duration"])
```

Each result contains sample indices, start and end times in seconds, and the
region duration.

## Generate a spectrogram

```python
from toolify.audio import get_spectrogram

get_spectrogram(
    "recording.wav",
    save_path="spectrogram.png",
    fft_size=2048,
    fig_size=(10, 4),
    show_save=(False, True),
)
```

The `show_save` tuple controls whether the plot is displayed and whether it is
saved.

## Read durations

```python
from toolify.audio import get_duration, get_total_duration

seconds = get_duration("recording.wav")
total_seconds = get_total_duration("dataset/audio", file_ext=".wav")
```

`get_total_duration` searches recursively and uses worker threads to inspect
matching files.
