from types import SimpleNamespace

import pytest

import toolify.youtube.youtube as youtube


VIDEO_ID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "value",
    [
        VIDEO_ID,
        f"https://www.youtube.com/watch?v={VIDEO_ID}&feature=share",
        f"https://youtu.be/{VIDEO_ID}?si=test",
        f"https://youtube.com/shorts/{VIDEO_ID}",
        f"youtube.com/embed/{VIDEO_ID}",
        f"https://m.youtube.com/live/{VIDEO_ID}",
    ],
)
def test_validate_url_supports_common_youtube_forms(value):
    assert youtube.validate_url(value) == VIDEO_ID


@pytest.mark.parametrize(
    "value",
    [
        "",
        "invalid",
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com/watch?v=too-short",
    ],
)
def test_validate_url_rejects_invalid_values(value):
    assert youtube.validate_url(value) is None


def test_convert_to_srt_supports_dicts_and_objects():
    subtitles = [
        {"text": "First line", "start": 0, "duration": 1.25},
        SimpleNamespace(text="Second line", start=61.5, duration=2.0),
    ]

    result = youtube.convert_to_srt(subtitles)

    assert "00:00:00,000 --> 00:00:01,250" in result
    assert "00:01:01,500 --> 00:01:03,500" in result
    assert "First line" in result
    assert result.endswith("\n")


def test_get_video_and_audio_qualities_prefers_separate_streams(monkeypatch):
    info = {
        "title": "Example",
        "formats": [
            {
                "format_id": "combined",
                "height": 720,
                "vcodec": "h264",
                "acodec": "aac",
                "abr": 128,
            },
            {
                "format_id": "video-720",
                "height": 720,
                "vcodec": "h264",
                "acodec": "none",
            },
            {
                "format_id": "video-1080",
                "height": 1080,
                "vcodec": "h264",
                "acodec": "none",
            },
            {
                "format_id": "audio-160",
                "vcodec": "none",
                "acodec": "opus",
                "abr": 160,
            },
        ],
    }

    class FakeYoutubeDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def extract_info(self, url, download):
            assert download is False
            return info

    monkeypatch.setattr(youtube.yt_dlp, "YoutubeDL", FakeYoutubeDL)

    metadata, videos, audios = youtube.get_video_and_audio_qualities(
        f"https://youtu.be/{VIDEO_ID}"
    )

    assert metadata == info
    assert videos == [("1080p", "video-1080"), ("720p", "video-720")]
    assert audios == [("160kbps", "audio-160")]


def test_get_transcript_uses_current_api_and_writes_srt(monkeypatch, tmp_path):
    calls = {}

    class FakeTranscript:
        def to_raw_data(self):
            return [{"text": "Hello", "start": 0.0, "duration": 1.0}]

    class FakeTranscriptApi:
        def fetch(self, video_id, languages):
            calls["video_id"] = video_id
            calls["languages"] = languages
            return FakeTranscript()

    monkeypatch.setattr(youtube, "YouTubeTranscriptApi", FakeTranscriptApi)

    path = youtube.get_transcript(
        VIDEO_ID,
        'Invalid:/Title?',
        output_path=str(tmp_path),
    )

    assert path == tmp_path / "Invalid__Title_.en.srt"
    assert path.read_text(encoding="utf-8").endswith("Hello\n")
    assert calls == {"video_id": VIDEO_ID, "languages": ["en-US", "en"]}


def test_download_best_quality_is_non_interactive(monkeypatch, tmp_path):
    calls = {}
    info = {"title": "Example"}

    monkeypatch.setattr(
        youtube,
        "get_video_and_audio_qualities",
        lambda url: (
            info,
            [("1080p", "video-1080"), ("720p", "video-720")],
            [("160kbps", "audio-160")],
        ),
    )

    def fake_download(url, video_format_id, audio_format_id, output_path):
        calls.update(
            {
                "url": url,
                "video_format_id": video_format_id,
                "audio_format_id": audio_format_id,
                "output_path": output_path,
            }
        )
        return "Example"

    monkeypatch.setattr(youtube, "download_video_and_audio", fake_download)

    result = youtube.download(
        VIDEO_ID,
        quality="best",
        subtitle=False,
        save_dir=str(tmp_path),
    )

    assert result == "Example"
    assert calls["video_format_id"] == "video-1080"
    assert calls["audio_format_id"] == "audio-160"
    assert calls["output_path"] == str(tmp_path)


def test_download_returns_none_for_unavailable_quality(monkeypatch, capsys):
    monkeypatch.setattr(
        youtube,
        "get_video_and_audio_qualities",
        lambda url: (
            {"title": "Example"},
            [("720p", "video-720")],
            [("128kbps", "audio-128")],
        ),
    )

    result = youtube.download(VIDEO_ID, quality="4k", subtitle=False)

    assert result is None
    assert "Available qualities: 720p" in capsys.readouterr().out
