import re
import os
# import srt
import yt_dlp
# from io import StringIO
# from datetime import timedelta
from youtube_transcript_api import YouTubeTranscriptApi


def validate_url(url):
    """Validate YouTube URL and extract video ID."""
    youtube_regex = (
        r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    )
    match = re.match(youtube_regex, url)
    if match:
        return match.group(4)  # Return video ID
    return None


def get_video_and_audio_qualities(url):
    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            # Collect video qualities
            video_qualities = []
            seen_resolutions = set()
            for f in formats:
                if f.get("vcodec") != "none" and f.get("height"):
                    resolution = f"{f['height']}p"
                    if resolution not in seen_resolutions:
                        video_qualities.append((resolution, f["format_id"]))
                        seen_resolutions.add(resolution)
            video_qualities.sort(key=lambda x: int(x[0][:-1]), reverse=True)

            # Collect audio qualities
            audio_qualities = []
            seen_bitrates = set()
            for f in formats:
                if f.get("acodec") != "none" and f.get("abr"):
                    bitrate = f"{int(f['abr'])}kbps"
                    if bitrate not in seen_bitrates:
                        audio_qualities.append((bitrate, f["format_id"]))
                        seen_bitrates.add(bitrate)
            audio_qualities.sort(key=lambda x: int(x[0][:-4]), reverse=True)

            return info, video_qualities, audio_qualities
    except Exception as e:
        print(f"Error fetching video/audio qualities: {str(e)}")
        return None, [], []


def download_video_and_audio(
    url, video_format_id, audio_format_id, output_path="downloads"
):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        ydl_opts = {
            "format": f"{video_format_id}+{audio_format_id}",
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_filename = f"{output_path}/{info['title']}.mp4"
            print(f"Video downloaded to {video_filename}")
            return info["title"]  # Return video title for SRT naming
    except Exception as e:
        print(f"Error downloading video/audio: {str(e)}")
        print("Ensure ffmpeg is installed and accessible in your PATH.")
        return None


def convert_to_srt(subtitles):
    """Convert YouTube transcript to SRT format"""
    srt_content = []
    for i, entry in enumerate(subtitles, start=1):
        start = entry["start"]
        end = start + entry["duration"]

        # Format time as SRT requires (HH:MM:SS,mmm)
        start_time = "{:02d}:{:02d}:{:06.3f}".format(
            int(start // 3600), int((start % 3600) // 60), start % 60
        ).replace(".", ",")

        end_time = "{:02d}:{:02d}:{:06.3f}".format(
            int(end // 3600), int((end % 3600) // 60), end % 60
        ).replace(".", ",")

        srt_content.append(f"{i}\n{start_time} --> {end_time}\n{entry['text']}\n")

    return "\n".join(srt_content)


def get_transcript(video_id, video_title, output_path="downloads"):
    try:
        try:
            subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=["en-US"])
        except:
            subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])

        srt_text = convert_to_srt(subtitles)
        subtitle_file = f"{output_path}/{video_title}.en.srt"
        with open(subtitle_file, "w", encoding="utf-8") as f:
            f.write(srt_text)

        print(f"Subtitles saved to {subtitle_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("This video might not have English subtitles available")


def download(url, quality=None, subtitle=True):

    video_id = validate_url(url)
    if not video_id:
        print(
            "Invalid YouTube URL. Please use a format like 'https://www.youtube.com/watch?v=VIDEO_ID' or 'https://youtu.be/VIDEO_ID'."
        )
        return

    info, video_qualities, audio_qualities = get_video_and_audio_qualities(url)

    if not info or not video_qualities or not audio_qualities:
        print("Failed to fetch video/audio details. Exiting...")
        return

    video_format_id = None
    # default is the best audio quality
    audio_format_id = audio_qualities[0][1]

    if quality:
        if quality == "best":
            video_format_id = video_qualities[0][1]  # quality is sorted so the first index is the best quality
        else:
            requested_tuple = next((tup for tup in video_qualities if tup[0] == quality), None)
            if requested_tuple:
                video_format_id = requested_tuple[1]
            else:
                print(f"Error: {quality} is not qvailable!")
                exit()  # or return
    else:
        try:
            for i, (resolution, format_id) in enumerate(video_qualities, 1):
                print(f"{i}. {resolution}")
            print("\nAvailable video qualities:")
            video_choice = int(input("\nSelect video quality (enter number): ")) - 1
            if not (0 <= video_choice < len(video_qualities)):
                print("Invalid selection. Exiting...")
                exit()

            for i, (bitrate, format_id) in enumerate(audio_qualities, 1):
                print(f"{i}. {bitrate}")
            print("\nAvailable audio qualities:")
            audio_choice = int(input("Select audio quality (enter number): ")) - 1
            if not (0 <= audio_choice < len(audio_qualities)):
                print("Invalid selection. Exiting...")
                exit()

        except Exception as e:
            print(f"Error: {str(e)}")
            print("Invalid selection, must be integer. Exiting...")
            exit()

        video_format_id = video_qualities[video_choice][1]
        audio_format_id = audio_qualities[audio_choice][1]

    #! needs to be changed
    print(f"Video Title: {info.get('title', 'Unknown')}")
    print(f"Video quality: {next((tup for tup in video_qualities if tup[1] == video_format_id), None)}")
    print(f"Audio quality: {next((tup for tup in audio_qualities if tup[1] == audio_format_id), None)}")
    
    # choice = input("download?(y/n)")
    choice = 'y'
    if choice == 'y':
        video_title = download_video_and_audio(url, video_format_id, audio_format_id)
        if subtitle and video_title:
            get_transcript(video_id, video_title)
    else:
        exit()

def get_youtube_playlist_info(playlist_url):
    """
    Fetches YouTube playlist info (name + video URLs) using yt-dlp.
    
    Args:
        playlist_url (str): URL of the YouTube playlist.
    
    Returns:
        dict: {
            "playlist_name": str,
            "video_urls": list[str]
        }
        Returns `None` if an error occurs.
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            playlist_name = playlist_info.get('title', 'Untitled Playlist')
            video_urls = [
                f"https://youtube.com/watch?v={video['id']}"
                for video in playlist_info['entries']
            ]
            
            return {
                "playlist_name": playlist_name,
                "video_urls": video_urls
            }
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return None


if __name__ == "__main__":
    #  How to use
    # For single video
    url = ""
    download(url, "720p")
    
    # For playlist
    # playlist_url = ""
    # playlist_data = get_youtube_playlist_info(playlist_url)
    # if playlist_data:
    #     print(f"Playlist Name: {playlist_data['playlist_name']}")
    #     print(f"Found {len(playlist_data['video_urls'])} videos:")
    #     for idx, url in enumerate(playlist_data['video_urls']):
    #         if idx == 0:
    #             continue
    #         print(url)
    #         download(url, "720p")
    # else:
    #     print("Failed to fetch playlist.")
