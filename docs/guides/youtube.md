# YouTube

YouTube utilities use yt-dlp for media and youtube-transcript-api for English
transcripts. FFmpeg is required when separate streams need to be merged.

## Download a video

```python
from toolify.youtube import download

download(
    "https://www.youtube.com/watch?v=XXXXXXXXXXX",
    quality="best",
    save_dir="downloads",
)
```

Select a resolution and skip transcript retrieval:

```python
download(
    "https://youtu.be/XXXXXXXXXXX",
    quality="720p",
    subtitle=False,
)
```

Numeric strings such as `"720"` are accepted. Omit `quality` to choose video
and audio formats interactively.

Supported inputs include watch, `youtu.be`, Shorts, embed, and live URLs, plus
raw 11-character video IDs.

## Inspect qualities

```python
from toolify.youtube import get_video_and_audio_qualities

info, video_qualities, audio_qualities = get_video_and_audio_qualities(
    "https://www.youtube.com/watch?v=XXXXXXXXXXX"
)
```

Quality lists contain `(label, format_id)` tuples ordered from highest to
lowest.

## Transcripts

```python
from toolify.youtube import get_transcript

subtitle_path = get_transcript(
    video_id="XXXXXXXXXXX",
    video_title="Example video",
    output_path="downloads",
    languages=("en-US", "en"),
)
```

Use `convert_to_srt` when transcript entries have already been retrieved.

## Playlists

```python
from toolify.youtube import get_youtube_playlist_info

playlist = get_youtube_playlist_info(
    "https://www.youtube.com/playlist?list=PLAYLIST_ID"
)
```

Playlist inspection returns its name and normalized video URLs without
downloading any media.
