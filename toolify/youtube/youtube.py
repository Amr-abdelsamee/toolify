"""YouTube download and transcript utilities.

The module uses :mod:`yt_dlp` to inspect and download videos and
:mod:`youtube_transcript_api` to save English transcripts as SRT files.

The main entry point is :func:`download`:

    >>> download("https://youtu.be/VIDEO_ID", quality="720p")

FFmpeg must be installed when yt-dlp needs to merge separate video and audio
streams.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


__all__ = [
    "validate_url",
    "get_video_and_audio_qualities",
    "download_video_and_audio",
    "convert_to_srt",
    "get_transcript",
    "download",
    "get_youtube_playlist_info",
]


FormatChoice = Tuple[str, str]

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_YOUTUBE_HOSTS = {"youtube.com", "m.youtube.com", "music.youtube.com"}
_PATH_BASED_VIDEO_ROUTES = {"embed", "live", "shorts", "v"}
_INVALID_FILENAME_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _is_video_id(value: str) -> bool:
    return bool(_VIDEO_ID_RE.fullmatch(value))


def validate_url(url: str) -> Optional[str]:
    """Extract a YouTube video ID from a URL.

    Supported forms include regular watch URLs, ``youtu.be`` links, Shorts,
    live, and embed URLs. A raw 11-character video ID is also accepted.

    Args:
        url: YouTube URL or raw video ID.

    Returns:
        The 11-character video ID, or ``None`` when the value is invalid.
    """
    if not isinstance(url, str):
        return None

    value = url.strip()
    if _is_video_id(value):
        return value

    # urlparse treats a URL without a scheme as a path.
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
        return video_id if _is_video_id(video_id) else None

    if host not in _YOUTUBE_HOSTS:
        return None

    query_video_id = parse_qs(parsed.query).get("v", [None])[0]
    if query_video_id and _is_video_id(query_video_id):
        return query_video_id

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) >= 2 and path_parts[0] in _PATH_BASED_VIDEO_ROUTES:
        return path_parts[1] if _is_video_id(path_parts[1]) else None

    return None


def _format_choices(
    formats: Sequence[Mapping[str, Any]],
) -> Tuple[List[FormatChoice], List[FormatChoice]]:
    """Build sorted, deduplicated video and audio format choices."""
    video_only = [
        item
        for item in formats
        if item.get("vcodec") != "none"
        and item.get("acodec") == "none"
        and item.get("height")
    ]
    audio_only = [
        item
        for item in formats
        if item.get("acodec") != "none"
        and item.get("vcodec") == "none"
        and item.get("abr")
    ]

    # Some extractors only expose combined formats, so retain a fallback.
    video_candidates = video_only or [
        item
        for item in formats
        if item.get("vcodec") != "none" and item.get("height")
    ]
    audio_candidates = audio_only or [
        item
        for item in formats
        if item.get("acodec") != "none" and item.get("abr")
    ]

    videos_by_height: Dict[int, str] = {}
    for item in video_candidates:
        format_id = item.get("format_id")
        if format_id is not None:
            videos_by_height[int(item["height"])] = str(format_id)

    audio_by_bitrate: Dict[int, str] = {}
    for item in audio_candidates:
        format_id = item.get("format_id")
        if format_id is not None:
            audio_by_bitrate[int(item["abr"])] = str(format_id)

    video_choices = [
        (f"{height}p", format_id)
        for height, format_id in sorted(videos_by_height.items(), reverse=True)
    ]
    audio_choices = [
        (f"{bitrate}kbps", format_id)
        for bitrate, format_id in sorted(audio_by_bitrate.items(), reverse=True)
    ]
    return video_choices, audio_choices


def get_video_and_audio_qualities(
    url: str,
) -> Tuple[Optional[Dict[str, Any]], List[FormatChoice], List[FormatChoice]]:
    """Inspect a video and return its available video and audio qualities.

    The returned choices are ``(label, format_id)`` tuples sorted from highest
    to lowest quality. Video-only and audio-only streams are preferred because
    they can be merged reliably by FFmpeg.

    Args:
        url: YouTube video URL.

    Returns:
        A tuple containing video metadata, video choices, and audio choices.
        On failure, returns ``(None, [], [])``.
    """
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        if not isinstance(info, dict):
            print("Could not read video metadata.")
            return None, [], []

        video_choices, audio_choices = _format_choices(info.get("formats", []))
        return info, video_choices, audio_choices
    except Exception as exc:
        print(f"Could not inspect the video: {exc}")
        return None, [], []


def download_video_and_audio(
    url: str,
    video_format_id: str,
    audio_format_id: Optional[str],
    output_path: str = "downloads",
) -> Optional[str]:
    """Download a video and merge its selected streams.

    Args:
        url: YouTube video URL.
        video_format_id: yt-dlp format ID for the video stream.
        audio_format_id: yt-dlp format ID for the audio stream. Pass ``None``
            when the selected video format already contains audio.
        output_path: Directory in which the media file will be saved.

    Returns:
        The downloaded video's title, or ``None`` if the download fails.
    """
    destination = Path(output_path)
    destination.mkdir(parents=True, exist_ok=True)

    format_selector = str(video_format_id)
    if audio_format_id and audio_format_id != video_format_id:
        format_selector = f"{video_format_id}+{audio_format_id}/best"

    options = {
        "format": format_selector,
        "paths": {"home": str(destination)},
        "outtmpl": {"default": "%(title)s [%(id)s].%(ext)s"},
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        title = info.get("title") if isinstance(info, dict) else None
        if title:
            print(f"Downloaded: {title}")
        return title
    except Exception as exc:
        print(f"Could not download the video: {exc}")
        print("If stream merging failed, ensure FFmpeg is installed and on PATH.")
        return None


def _transcript_value(entry: Any, name: str) -> Any:
    if isinstance(entry, Mapping):
        return entry[name]
    return getattr(entry, name)


def _srt_timestamp(seconds: float) -> str:
    total_milliseconds = max(0, round(float(seconds) * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def convert_to_srt(subtitles: Sequence[Any]) -> str:
    """Convert transcript entries to SubRip (SRT) text.

    Entries may be dictionaries or objects with ``text``, ``start``, and
    ``duration`` attributes, allowing this helper to work with both raw data
    and transcript objects.

    Args:
        subtitles: Transcript entries in chronological order.

    Returns:
        Complete UTF-8-compatible SRT content.
    """
    blocks = []
    for index, entry in enumerate(subtitles, start=1):
        start = float(_transcript_value(entry, "start"))
        end = start + float(_transcript_value(entry, "duration"))
        text = str(_transcript_value(entry, "text")).strip()
        blocks.append(
            f"{index}\n{_srt_timestamp(start)} --> {_srt_timestamp(end)}\n{text}"
        )

    return "\n\n".join(blocks) + ("\n" if blocks else "")


def _safe_filename(value: str, fallback: str) -> str:
    safe_value = _INVALID_FILENAME_CHARS_RE.sub("_", value).strip(" .")
    return safe_value or fallback


def get_transcript(
    video_id: str,
    video_title: str,
    output_path: str = "downloads",
    languages: Sequence[str] = ("en-US", "en"),
) -> Optional[Path]:
    """Download a transcript and save it as an SRT file.

    Args:
        video_id: The video's 11-character YouTube ID.
        video_title: Title used to name the subtitle file.
        output_path: Directory in which the SRT file will be saved.
        languages: Preferred transcript language codes, in priority order.

    Returns:
        The saved SRT path, or ``None`` if no transcript could be retrieved.
    """
    destination = Path(output_path)
    destination.mkdir(parents=True, exist_ok=True)

    try:
        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=list(languages),
        )
        entries = (
            transcript.to_raw_data()
            if hasattr(transcript, "to_raw_data")
            else list(transcript)
        )

        subtitle_path = destination / (
            f"{_safe_filename(video_title, video_id)}.en.srt"
        )
        subtitle_path.write_text(convert_to_srt(entries), encoding="utf-8")
        print(f"Subtitles saved to: {subtitle_path}")
        return subtitle_path
    except Exception as exc:
        print(f"Could not download subtitles: {exc}")
        return None


def _prompt_for_choice(label: str, choices: Sequence[FormatChoice]) -> FormatChoice:
    print(f"\nAvailable {label} qualities:")
    for index, (quality, _) in enumerate(choices, start=1):
        print(f"{index}. {quality}")

    selection = int(input(f"Select {label} quality (enter number): ")) - 1
    if not 0 <= selection < len(choices):
        raise ValueError(f"Invalid {label} quality selection.")
    return choices[selection]


def download(
    url: str,
    quality: Optional[str] = None,
    subtitle: bool = True,
    save_dir: str = "downloads",
) -> Optional[str]:
    """Download one YouTube video, optionally with an English transcript.

    If ``quality`` is omitted, the function interactively asks for video and
    audio qualities. Use ``"best"`` for the highest available video quality,
    or a resolution such as ``"720p"``. The highest available audio quality is
    selected automatically when ``quality`` is supplied.

    Args:
        url: YouTube video URL or raw video ID.
        quality: ``None`` for interactive selection, ``"best"``, or a
            resolution such as ``"1080p"``.
        subtitle: If true, save an English SRT transcript when available.
        save_dir: Directory in which media and subtitle files will be saved.

    Returns:
        The downloaded video's title, or ``None`` when validation, selection,
        inspection, or downloading fails.
    """
    video_id = validate_url(url)
    if not video_id:
        print("Invalid YouTube URL or video ID.")
        return None

    normalized_url = f"https://www.youtube.com/watch?v={video_id}"
    info, video_choices, audio_choices = get_video_and_audio_qualities(
        normalized_url
    )
    if not info or not video_choices or not audio_choices:
        print("No downloadable video/audio formats were found.")
        return None

    try:
        if quality is None:
            video_label, video_format_id = _prompt_for_choice(
                "video", video_choices
            )
            audio_label, audio_format_id = _prompt_for_choice(
                "audio", audio_choices
            )
        else:
            requested_quality = str(quality).strip().lower()
            if requested_quality.isdigit():
                requested_quality += "p"

            if requested_quality == "best":
                video_label, video_format_id = video_choices[0]
            else:
                match = next(
                    (
                        choice
                        for choice in video_choices
                        if choice[0].lower() == requested_quality
                    ),
                    None,
                )
                if match is None:
                    available = ", ".join(label for label, _ in video_choices)
                    print(
                        f"Video quality {quality!r} is unavailable. "
                        f"Available qualities: {available}"
                    )
                    return None
                video_label, video_format_id = match

            audio_label, audio_format_id = audio_choices[0]
    except (TypeError, ValueError) as exc:
        print(f"Invalid selection: {exc}")
        return None

    print(f"Video: {info.get('title', 'Unknown')}")
    print(f"Selected video quality: {video_label}")
    print(f"Selected audio quality: {audio_label}")

    video_title = download_video_and_audio(
        normalized_url,
        video_format_id,
        audio_format_id,
        output_path=save_dir,
    )
    if video_title and subtitle:
        get_transcript(video_id, video_title, output_path=save_dir)

    return video_title


def get_youtube_playlist_info(
    playlist_url: str,
) -> Optional[Dict[str, Any]]:
    """Return a playlist's title and video URLs without downloading it.

    Args:
        playlist_url: YouTube playlist URL.

    Returns:
        A dictionary with ``playlist_name`` and ``video_urls`` keys, or
        ``None`` if the playlist cannot be inspected.
    """
    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)

        if not isinstance(playlist_info, dict):
            return None

        video_urls = [
            f"https://www.youtube.com/watch?v={entry['id']}"
            for entry in playlist_info.get("entries") or []
            if entry and _is_video_id(str(entry.get("id", "")))
        ]
        return {
            "playlist_name": playlist_info.get("title", "Untitled Playlist"),
            "video_urls": video_urls,
        }
    except Exception as exc:
        print(f"Could not inspect the playlist: {exc}")
        return None
