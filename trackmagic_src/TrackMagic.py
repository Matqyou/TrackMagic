""" TrackMagic is a YouTube video/audio downloader.
 By default, it downloads the highest quality video with
  an upper limit of 1080p and best audio available.

 Use it on individual videos or entire playlists.

Issues:
 - Does not support EC3/AC3 and 6 channel audio (not fully tested)

Dependencies:
 - yt_dlp used to download YouTube streams.
 - FFmpeg used to convert and merge streams.

Made by mαtq on Discord
"""
import urllib.parse

from classes.static.UserChoice import StreamResult, UserChoice
from classes.static.Configuration import Configuration
from classes.static.UserInput import UserInput
from classes.Logger import Logger, Launcher
from classes.static.Utils import Utils
from urllib import parse
import subprocess
import requests
import atexit
import sys
import os

LAUNCHER: Launcher = Launcher()
LOGGER: Logger = LAUNCHER.logger
LOGGER.set_log_to_file(True)

try:
    from classes.static.ImageProcessing import ImageProcessing
    from classes.static.FileExplorer import FileExplorer
    from classes.static.Downloader import Downloader
    from classes.Records import Records, Record
    from classes.static.FFmpeg import FFmpeg
    import win32clipboard
    import yt_dlp as youtube  # type: ignore
    import ffmpy
except ModuleNotFoundError as e:
    LOGGER.log('LIBRARIES', 'Installing libraries..')
    LOGGER.log('LIBRARIES', f'Reason: {e}')
    subprocess.call(['pip', 'install', '-r', '..\\requirements.txt'])
    LOGGER.log('LIBRARIES', 'Installed successfully!')
    subprocess.call([sys.executable] + sys.argv)
    exit()
except Exception as e:
    LOGGER.log('LIBRARIES', f'Error: {e}')
    exit()


class TrackMagic:
    def __init__(self):
        self.storage: Records = None  # type: ignore

    def init(self) -> None:
        FFmpeg.init(LOGGER)
        FFmpeg.check_ffmpeg()

        self.storage = Records(LOGGER)
        self.storage.load_records()

    @staticmethod
    def _find_thumbnail(thumbnails: list[dict]) -> tuple[str, bytes]:
        for thumbnail in sorted(thumbnails, key=lambda x: int(x['id']), reverse=True):
            thumbnail_url: str = thumbnail['url']

            response = requests.get(thumbnail_url)
            if response.status_code == 404:
                continue

            if response.status_code == 200:
                return thumbnail_url, response.content
            else:
                raise Exception(f'Other status code than 200 and 404 received: {response.status_code}')
        return None, None  # type: ignore

    @staticmethod
    def _choose_best_stream(streams: dict, stream_choice: int) -> tuple[int, tuple]:
        filtered_streams = filter(
            lambda x: True if x.get("format_note") != 'Premium' and x.get("filesize") is not None else False, streams)
        sorted_by_resolution = sorted(filtered_streams,
                                      key=lambda x: (Utils.none_to_zero(x.get('height')),
                                                     Utils.none_to_zero(x.get('filesize'))),
                                      reverse=True)

        progressive_candidate = None
        interlaced_video = None
        interlaced_audio = None
        for stream in sorted_by_resolution:
            video_codec = stream.get('vcodec')
            audio_codec = stream.get('acodec')
            if video_codec != 'none' and audio_codec != 'none' and progressive_candidate is None:
                progressive_candidate = stream
            elif video_codec != 'none' and audio_codec == 'none' and interlaced_video is None:
                interlaced_video = stream
            elif video_codec == 'none' and not audio_codec in ('none', 'ec-3') and stream.get('audio_channels', None) != 6 and interlaced_audio is None:  # todo: more test cases
                interlaced_audio = stream

            if interlaced_video is not None and interlaced_audio is not None:
                break

        if stream_choice == UserChoice.VIDEO:
            if interlaced_video is None or progressive_candidate is not None and progressive_candidate['height'] > \
                    interlaced_video['height']:
                return StreamResult.PROGRESSIVE_VIDEO, (progressive_candidate,)
            elif interlaced_video is not None:
                return StreamResult.INTERLACED_VIDEO_ONLY, (interlaced_video,)
            else:
                return StreamResult.NO_STREAM, None  # type: ignore

        elif stream_choice == UserChoice.AUDIO:
            if interlaced_audio is not None:
                return StreamResult.INTERLACED_AUDIO_ONLY, (interlaced_audio,)
            elif progressive_candidate is not None:
                return StreamResult.PROGRESSIVE_VIDEO, (progressive_candidate,)
            return StreamResult.NO_STREAM, None  # type: ignore

        elif stream_choice == UserChoice.VIDEO_AND_AUDIO:
            if interlaced_video is not None and interlaced_audio is not None:
                return StreamResult.INTERLACED_VIDEO_AUDIO, (interlaced_video, interlaced_audio)
            elif progressive_candidate is not None:
                return StreamResult.PROGRESSIVE_VIDEO, (progressive_candidate,)
            else:
                return StreamResult.NO_STREAM, None  # type: ignore

    def order_playlist(self, playlist_url: str, user_choice: int) -> None:
        with youtube.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            for video_entry in info['entries']:
                video_url = f'https://www.youtube.com/watch?v={video_entry["id"]}'
                self.order(video_url, user_choice, False)

    def order(self, video_url: str, user_choice: int, big_info: bool = True) -> None:
        video_id: str = Utils.get_video_id_from_url(video_url)
        data_record: Record = self.storage.get_record(video_id)
        if data_record is None:
            data_record = Record()
            data_record.video_id = video_id
        else:
            if data_record.check_file_integrity():  # files are missing, forget them
                self.storage.save_records()

        video_wanted = user_choice == UserChoice.VIDEO or user_choice == UserChoice.VIDEO_AND_AUDIO
        audio_wanted = user_choice == UserChoice.AUDIO or user_choice == UserChoice.VIDEO_AND_AUDIO
        video_on_disk = data_record.video
        audio_on_disk = data_record.audio

        video_needed = video_on_disk is None and video_wanted
        audio_needed = audio_on_disk is None and audio_wanted

        ordered_string = ("Video", "Audio", "Video and Audio")[user_choice]
        if big_info:
            LOGGER.log('Order', f'Ordered {ordered_string} from `{Utils.get_video_id_from_url(video_url)}`')
            LOGGER.log('Order', f'Video: {video_on_disk}')
            LOGGER.log('Order', f'Audio: {audio_on_disk}')
            LOGGER.log('Order', f'')

        if not video_needed and not audio_needed:
            LOGGER.log('Order', f'Ordered {ordered_string} from `{video_id}` | No work to do on {data_record.title}')
            return

        with youtube.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
            except youtube.utils.DownloadError as e:
                LOGGER.log('Order', f'Ordered {ordered_string} from `{video_id}` | {e}')
                return
            streams = info.get('formats', []) + info.get('adaptive_fmts', [])

        video_title: str = info.get('title', None)
        video_length: int = info.get('duration', None)
        if big_info:
            LOGGER.log('Order', f'Title: {video_title}')
            LOGGER.log('Order', f'Length: {video_length}')

        thumbnail_path: str = None  # type: ignore
        thumbnail_url, thumbnail = TrackMagic._find_thumbnail(info['thumbnails'])
        if thumbnail:
            purl = parse.urlparse(thumbnail_url)
            url_path = purl.path

            thumbnail_extension = url_path[url_path.rfind('.'):]
            thumbnail_path = os.path.join(Configuration.temp_dir, f'thumbnail{thumbnail_extension}')
            FileExplorer.create_folder(Configuration.temp_dir)
            with open(thumbnail_path, 'wb') as file:
                file.write(thumbnail)
            thumbnail_path = ImageProcessing.convert_to_jpg(thumbnail_path)
            data_record.thumbnail = thumbnail_url

        stream_result: int = None  # type: ignore
        stream_choices: tuple[dict] = None  # type: ignore
        if video_needed and audio_needed:
            if big_info:
                LOGGER.log('Order', f'Searching video and audio..')
            stream_result, stream_choices = TrackMagic._choose_best_stream(streams, UserChoice.VIDEO_AND_AUDIO)
        elif video_needed:
            if big_info:
                LOGGER.log('Order', f'Searching video..')
            stream_result, stream_choices = TrackMagic._choose_best_stream(streams, UserChoice.VIDEO)
            if stream_result == StreamResult.INTERLACED_VIDEO_ONLY and audio_on_disk is None:
                if big_info:
                    LOGGER.log('Order', f'Nevermind, found interlaced video WITHOUT audio.')
                    LOGGER.log('Order', f'Searching video and audio..')
                stream_result, stream_choices = TrackMagic._choose_best_stream(streams, UserChoice.VIDEO_AND_AUDIO)
        elif audio_needed:
            if big_info:
                LOGGER.log('Order', f'Searching audio..')
            stream_result, stream_choices = TrackMagic._choose_best_stream(streams, UserChoice.AUDIO)

        if stream_result == StreamResult.PROGRESSIVE_VIDEO:
            if big_info:
                LOGGER.log('Order', f'Progressive video has been found!')
                LOGGER.log('Order', f'Downloading progressive video..')
            progressive_format_id = stream_choices[0]['format_id']
            original_progressive = Downloader.download_stream(progressive_format_id, video_url)
            if audio_needed:
                if big_info:
                    LOGGER.log('Order', f'Extracting audio from video..')
                audio_extracted = FFmpeg.process_audio_from_video(original_progressive)
                audio_path = FileExplorer.move_to_folder(audio_extracted, Configuration.audio_dir, original_progressive)
                data_record.audio = audio_path
                data_record.audio_stream = progressive_format_id
            if video_needed:
                video_path = FileExplorer.move_to_folder(original_progressive, Configuration.video_dir)
                data_record.video = video_path
                data_record.video_stream = progressive_format_id

        elif stream_result == StreamResult.INTERLACED_VIDEO_AUDIO:
            if big_info:
                LOGGER.log('Order', f'Interlaced video and audio have been found!')
                LOGGER.log('Order', f'Downloading interlaced audio..')
            video_format_id = stream_choices[0]['format_id']
            audio_format_id = stream_choices[1]['format_id']

            original_audio = Downloader.download_stream(audio_format_id, video_url)
            if big_info:
                LOGGER.log('Order', f'Converting audio file..')
            converted_audio = FFmpeg.convert_audio(original_audio)
            if audio_needed:
                audio_thumbnail = FFmpeg.add_thumbnail_to_media_file(converted_audio, thumbnail_path)
                audio_path = FileExplorer.move_to_folder(audio_thumbnail, Configuration.audio_dir, original_audio)
                data_record.audio = audio_path
                data_record.audio_stream = audio_format_id
            if video_needed:
                if big_info:
                    LOGGER.log('Order', f'Downloading interlaced video..')
                original_video = Downloader.download_stream(video_format_id, video_url)
                if big_info:
                    LOGGER.log('Order', f'Merging video and audio..')
                video_merged = FFmpeg.merge_video_audio(original_video, converted_audio)
                video_thumbnail = FFmpeg.add_thumbnail_to_media_file(video_merged, thumbnail_path)
                FileExplorer.create_folder(Configuration.video_dir)
                video_path = FileExplorer.move_to_folder(video_thumbnail, Configuration.video_dir, original_video)
                data_record.video = video_path
                data_record.video_stream = video_format_id

        elif stream_result == StreamResult.INTERLACED_VIDEO_ONLY:  # audio_on_disk must exist to get here
            if big_info:
                LOGGER.log('Order', f'Interlaced video has been found!')
                LOGGER.log('Order', f'Downloading interlaced video..')
            if video_needed:
                video_format_id = stream_choices[0]['format_id']
                original_video = Downloader.download_stream(video_format_id, video_url)
                if big_info:
                    LOGGER.log('Order', f'Merging video and audio(on disk)..')
                video_merged = FFmpeg.merge_video_audio(original_video, audio_on_disk)
                video_thumbnail = FFmpeg.add_thumbnail_to_media_file(video_merged, thumbnail_path)
                FileExplorer.create_folder(Configuration.video_dir)
                video_path = FileExplorer.move_to_folder(video_thumbnail, Configuration.video_dir, original_video)
                data_record.video = video_path
                data_record.video_stream = video_format_id

        elif stream_result == StreamResult.INTERLACED_AUDIO_ONLY:
            if big_info:
                LOGGER.log('Order', f'Interlaced audio has been found!')
                LOGGER.log('Order', f'Downloading interlaced audio..')
            if audio_needed:
                audio_format_id = stream_choices[0]['format_id']
                original_audio = Downloader.download_stream(audio_format_id, video_url)
                if big_info:
                    LOGGER.log('Order', f'Converting audio file..')
                audio_converted = FFmpeg.convert_audio(original_audio)
                audio_thumbnail = FFmpeg.add_thumbnail_to_media_file(audio_converted, thumbnail_path)
                audio_path = FileExplorer.move_to_folder(audio_thumbnail, Configuration.audio_dir, original_audio)
                data_record.audio = audio_path
                data_record.audio_stream = audio_format_id

        elif stream_result == StreamResult.NO_STREAM:
            LOGGER.log('TrackMagic', f'Ordered {ordered_string} from `{video_id}` | Weirdly no streams were found for the user')
            return

        LOGGER.log('Order', f'Ordered {ordered_string} from `{video_id}` | {video_title} is done!')
        data_record.title = video_title
        data_record.length = video_length
        self.storage.update_record(data_record)
        self.storage.save_records()
        FileExplorer.cleanup_temp()


def main():
    instance = TrackMagic()
    instance.init()

    instance.storage.check_integrity()

    advanced = False
    while True:
        print()
        print('To start downloading video/audio, please provide the url of the video or playlist:')
        print('(note if you want to download a playlist, make sure the url starts as follows:')
        print(' https://youtube.com/playlist?list=PLAYLIST_ID)')
        print()
        if not advanced:
            print(' or enable [A]dvanced mode')
        else:
            print(' Advanced mode enabled')

        media_url = input('> ')

        if media_url.lower() == 'a':
            advanced = True
            continue

        purl = parse.urlparse(media_url)
        url_path = purl.path
        if url_path == '/watch' or media_url.startswith('https://youtu.be/'):
            url_type = 0
            print('URL type is a video')
        elif url_path == '/playlist':
            url_type = 1
            print('URL type is a playlist')
        else:
            raise Exception(f'Could not detect url type: {media_url}')

        print()
        print('Now pick the type of media:')
        print('[V]ideo or [A]udio (or [B]oth)')
        media_type = UserInput.choice_lowercase(['v', 'a', 'b'], '> ')

        if media_type == 'v':
            user_choice = UserChoice.VIDEO
            print(f'Picked video media type (current extension type {FFmpeg.get_video_extension()})')
            if advanced:
                print()
                print('Change video extension?')
                print('Enter nothing to skip..')
                new_extension = input('> ')
                if new_extension:
                    FFmpeg.set_video_extension(new_extension)
        elif media_type == 'a':
            user_choice = UserChoice.AUDIO
            print(f'Picked audio media type (current extension type {FFmpeg.get_audio_extension()})')
            if advanced:
                print()
                print('Change audio extension?')
                print('Enter nothing to skip..')
                new_extension = input('> ')
                if new_extension:
                    FFmpeg.set_audio_extension(new_extension)
        elif media_type == 'b':
            user_choice = UserChoice.VIDEO_AND_AUDIO
            print('Picked video and audio media types')
        else:
            raise Exception(f'Invalid media type provided by user: {media_type}')

        order_func = (instance.order, instance.order_playlist)[url_type]
        order_func(media_url, user_choice)


def cleanup():
    FileExplorer.cleanup_temp()


if __name__ == '__main__':
    atexit.register(cleanup)
    main()
