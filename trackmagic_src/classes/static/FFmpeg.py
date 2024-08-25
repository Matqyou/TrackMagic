from classes.static.Configuration import Configuration
from classes.Logger import Logger
import subprocess
import ffmpy
import os


class FFmpeg:
    logger: Logger = None  # type: ignore

    @staticmethod
    def init(logger: Logger) -> None:
        FFmpeg.logger = logger

    @staticmethod
    def check_ffmpeg():
        try:
            current_directory = os.getcwd()
            ffmpeg_local_path = os.path.join(current_directory, '../ffmpeg.exe')

            # Check in the current directory first
            if os.path.exists(ffmpeg_local_path):
                ffmpeg_env = ffmpeg_local_path
                ffmpy.executable = ffmpeg_local_path
            else:
                ffmpeg_env = os.getenv('FFMPEG_BINARY', 'ffmpeg')
            exit_code = subprocess.call([ffmpeg_env, '-version', '-loglevel panic'], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            FFmpeg.logger.log('FFmpeg', 'FFmpeg was not found on your system')
            FFmpeg.logger.log('FFmpeg', 'Either you\'ve never downloaded FFmpeg')
            FFmpeg.logger.log('FFmpeg', ' or you haven\'t added it to PATH')
            FFmpeg.logger.log('FFmpeg', '')
            FFmpeg.logger.log('FFmpeg', 'Check readme.md for more information')
            exit(-1)

    # @staticmethod
    # def process_video_stream(video_stream, progressive: bool):
    #     video_at = video_stream.download(Configuration.temp_video_dir)
    #     video_file = os.path.basename(video_at)
    #     video_filename, video_ext = os.path.splitext(video_file)
    #     if not progressive:
    #         return video_at
    #
    #     video_path = f'{Configuration.video_dir}{video_filename}.mp4'
    #     ffmpeg = ffmpy.FFmpeg(inputs={video_at: None},
    #                           outputs={video_path: None},
    #                           global_options='-y -loglevel warning')
    #     ffmpeg.run()
    #     os.remove(video_at)
    #     return video_path

    @staticmethod
    def process_audio_from_video(video_path: str):
        video_directory = os.path.abspath(video_path)
        video_file = os.path.basename(video_path)
        video_filename, _ = os.path.splitext(video_file)

        audio_path = os.path.join(video_directory, f'{video_filename}.{Configuration.audio_ext}')

        ffmpeg = ffmpy.FFmpeg(inputs={video_path: None},
                              outputs={audio_path: None},
                              global_options='-y -loglevel warning')
        ffmpeg.run()
        return audio_path

    @staticmethod
    def convert_audio(audio_path: str):
        audio_directory = os.path.dirname(audio_path)
        audio_file = os.path.basename(audio_path)
        audio_filename, audio_extension = os.path.splitext(audio_file)

        if audio_extension == Configuration.audio_ext:
            return audio_path

        new_audio_path = os.path.join(audio_directory, f'{audio_filename}{Configuration.audio_ext}')

        ffmpeg = ffmpy.FFmpeg(inputs={audio_path: None},
                              outputs={new_audio_path: None},
                              global_options='-y -loglevel warning')
        ffmpeg.run()
        return new_audio_path

    @staticmethod
    def merge_video_audio(video_path: str, audio_path: str):
        video_directory = os.path.dirname(video_path)
        video_file = os.path.basename(video_path)
        video_filename, _ = os.path.splitext(video_file)
        new_video_path = os.path.join(video_directory, f'{video_filename}.merge.mp4')

        ffmpeg = ffmpy.FFmpeg(inputs={video_path: None, audio_path: None},
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
            ffmpeg = ffmpy.FFmpeg(inputs={media_path: None, thumbnail_path: None},
                                  outputs={new_media_path: '-map 1 -map 0 -c copy -disposition:0 attached_pic'},
                                  global_options='-y -loglevel warning')
            ffmpeg.run()
        except ffmpy.FFRuntimeError:
            return media_path

        return new_media_path
