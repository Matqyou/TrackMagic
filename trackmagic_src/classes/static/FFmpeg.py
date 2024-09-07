from classes.static.Configuration import Configuration
from classes.Logger import Logger
import subprocess
import ffmpy
import os


class FFmpeg:
    executable: str = None  # type: ignore
    logger: Logger = None  # type: ignore
    audio_extension: str = None  # type: ignore
    video_extension: str = None  # type: ignore

    @staticmethod
    def init(logger: Logger) -> None:
        FFmpeg.logger = logger
        FFmpeg.audio_extension = Configuration.audio_ext
        FFmpeg.video_extension = Configuration.video_ext

    @staticmethod
    def set_audio_extension(new_extension: str) -> None:
        FFmpeg.audio_extension = new_extension

    @staticmethod
    def get_audio_extension() -> str:
        return FFmpeg.audio_extension

    @staticmethod
    def set_video_extension(new_extension: str) -> None:
        FFmpeg.video_extension = new_extension

    @staticmethod
    def get_video_extension() -> str:
        return FFmpeg.video_extension

    @staticmethod
    def check_ffmpeg():
        try:
            current_directory = os.getcwd()
            ffmpeg_local_path = os.path.join(current_directory, '..', 'ffmpeg.exe')

            # Check in the current directory first
            if os.path.exists(ffmpeg_local_path):
                FFmpeg.executable = ffmpeg_local_path
            else:
                FFmpeg.executable = 'ffmpeg'
            subprocess.call([FFmpeg.executable, '-version', '-loglevel panic'], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            FFmpeg.logger.log('FFmpeg', 'FFmpeg was not found on your system')
            FFmpeg.logger.log('FFmpeg', 'Either you\'ve never downloaded FFmpeg')
            FFmpeg.logger.log('FFmpeg', ' or you haven\'t added it to PATH')
            FFmpeg.logger.log('FFmpeg', '')
            FFmpeg.logger.log('FFmpeg', 'Check readme.md for more information')
            exit(-1)

    @staticmethod
    def process_audio_from_video(video_path: str):
        video_directory = os.path.abspath(video_path)
        video_file = os.path.basename(video_path)
        video_filename, _ = os.path.splitext(video_file)

        audio_path = os.path.join(video_directory, f'{video_filename}.{FFmpeg.audio_extension}')

        ffmpeg = ffmpy.FFmpeg(executable=FFmpeg.executable,
                              inputs={video_path: None},
                              outputs={audio_path: None},
                              global_options='-y -loglevel warning')
        ffmpeg.run()
        return audio_path

    @staticmethod
    def convert_audio(audio_path: str):  # todo: same for progressive videos, dont know if they will be mp4 100% of the time
        audio_directory = os.path.dirname(audio_path)
        audio_file = os.path.basename(audio_path)
        audio_filename, audio_extension = os.path.splitext(audio_file)

        if audio_extension == FFmpeg.audio_extension:
            return audio_path

        new_audio_path = os.path.join(audio_directory, f'{audio_filename}{FFmpeg.audio_extension}')
        print(new_audio_path)

        ffmpeg = ffmpy.FFmpeg(executable=FFmpeg.executable,
                              inputs={audio_path: None},
                              outputs={new_audio_path: None},
                              global_options='-y -loglevel warning')
        ffmpeg.run()
        return new_audio_path

    @staticmethod
    def merge_video_audio(video_path: str, audio_path: str):
        video_directory = os.path.dirname(video_path)
        video_file = os.path.basename(video_path)
        video_filename, _ = os.path.splitext(video_file)
        new_video_path = os.path.join(video_directory, f'{video_filename}.merge.{FFmpeg.video_extension}')

        ffmpeg = ffmpy.FFmpeg(executable=FFmpeg.executable,
                              inputs={video_path: None, audio_path: None},
                              outputs={new_video_path: '-c copy -map 0:v:0 -map 1:a:0'},
                              global_options='-y -loglevel warning')
        ffmpeg.run()
        return new_video_path

    @staticmethod
    def add_thumbnail_to_media_file(media_path: str, thumbnail_path: str):  # Either video or audio (apparently)
        if thumbnail_path is None:
            return media_path

        media_directory = os.path.dirname(media_path)
        media_file = os.path.basename(media_path)
        media_filename, media_extension = os.path.splitext(media_file)
        new_media_path = os.path.join(media_directory, f'{media_filename}.thumbnail{media_extension}')

        try:
            ffmpeg = ffmpy.FFmpeg(executable=FFmpeg.executable,
                                  inputs={media_path: None, thumbnail_path: None},
                                  outputs={new_media_path: '-map 1 -map 0 -c copy -disposition:0 attached_pic'},
                                  global_options='-y -loglevel warning')
            ffmpeg.run()
        except ffmpy.FFRuntimeError:
            return media_path

        return new_media_path
