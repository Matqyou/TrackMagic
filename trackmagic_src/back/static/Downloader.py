from back.static.Configuration import Configuration
import yt_dlp as youtube
import os

from back.static.FFmpeg import FFmpeg
class Downloader:
    ffmpeg_location: str = None  # type: ignore
    stream_filepath: str = None  # type: ignore
    stream_filename: str = None  # type: ignore

    @staticmethod
    def set_ffmpeg_location(ffmpeg_location: str) -> None:
        Downloader.ffmpeg_location = ffmpeg_location

    @staticmethod
    def _set_stream_filepath_hook(data: dict) -> None:
        if data['status'] == 'finished':
            Downloader.stream_filepath = data['info_dict']['filename']
            Downloader.stream_filename = os.path.basename(Downloader.stream_filepath)

    @staticmethod
    def download_stream(format_id: str, video_url: str) -> str:
        downloader_options = {'ffmpeg_location': FFmpeg.get_executable(),
                              'outtmpl': f'{Configuration.temp_dir}%(title)s.%(ext)s',
                              'progress_hooks': [Downloader._set_stream_filepath_hook],
                              'format': format_id,
                              'noplaylist': True,
                              'quiet': True}

        with youtube.YoutubeDL(downloader_options) as ydl:
            ydl.download(video_url)

        return Downloader.stream_filepath
