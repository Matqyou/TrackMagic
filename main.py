""" Youtube maximum quality downloader application.
Supports individual links to videos and playlists.

Downloads videos with highest quality possible and
 saves a seperate audio file with it.

Dependencies:
 - pytube used to download YouTube streams. (pip install pytube)
 - FFmpeg used to convert and merge streams.

Made by matq on Discord
User ID 243713302750953482 on https://discord.id/ & https://lookup.guru/
"""

from Record import *
import pytube
import ffmpy
import os

ALLOWED_KEYS = [
    'video_id',
    'title',
    'length',
    'progressive',
    'video',
    'video_stream',
    'audio',
    'audio_stream'
]

records = {}
RECORDS_FILE = 'records'
VIDEO_DIR = 'Videos\\'
TRACK_DIR = 'Audio\\'
TEMP_DIR = 'Temp\\'
TEMP_VIDEO_DIR = TEMP_DIR + 'Video\\'
TEMP_TRACK_DIR = TEMP_DIR + 'Audio\\'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESETCOLOR = '\033[39m'
RESETBGCOLOR = '\033[49m'
RESET = '\033[0m'
UNDERLINE = '\033[4m'
UNUNDERLINE = '\033[24m'
BOLD = '\033[1m'
UNBOLD = '\033[2m'


def cleanup_temp():
    path = f'{os.getcwd()}\\{TEMP_DIR}'
    if os.path.exists(path):
        for subdir in os.listdir(path):
            subdir = f'{path}{subdir}\\'
            for file in os.listdir(subdir):
                os.remove(subdir + file)
            os.rmdir(subdir)
        os.rmdir(path)


def background_color(r: int, g: int, b: int):
    print(f'\033[48;2;{r};{g};{b}m', end='')


def input_choice(choices, transform, prompt):
    while True:
        user_input = transform(input(prompt))
        if not user_input:
            continue

        if user_input in choices:
            return user_input


def update_records():
    global records
    new_content = ''
    for record in records.values():
        new_content += record.Parse()

    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)


def stream_is_progressive(stream: pytube.Stream):
    return stream.video_codec is not None and stream.audio_codec is not None


# def process_playlist(playlist_url: str):
#     playlist = pytube.Playlist(playlist_url)
#     print(f'Playlist {playlist.title} with video count of {playlist.length}')
#
#     for i, session in enumerate(playlist.videos):
#         if i % 2:
#             background_color(50, 50, 50)
#         else:
#             background_color(30, 30, 30)
#
#         process_video(session)


def process_video(video_string: str, auto_video=False, auto_audio=False):
    try:
        session = pytube.YouTube(url=video_string)
    except:
        try:
            session = pytube.YouTube(url=f'https://www.youtube.com/watch?v={video_string}')
        except:
            print('Invalid video string supplied'); return

    video_id = session.video_id
    id_text = f'{UNDERLINE}{video_id}{UNUNDERLINE}'

    video_updated = False
    video_exists = False
    audio_updated = False
    audio_exists = False

    if video_id in records:  # Existing record
        index_text = f'Loaded #{list(records).index(video_id)}'
        record = records[video_id]

        video_exists = record.video is not None
        audio_exists = record.audio is not None

        if video_exists and not os.path.exists(record.video):
            video_exists = False
            print('Video file couldn\'t be found..')
        if audio_exists and not os.path.exists(record.audio):
            audio_exists = False
            print('Audio file couldn\'t be found..')
    else:  # New record
        index_text = f'Created #{len(records)}'
        record = Record()
        record.video_id = video_id
        record.title = session.title
        record.length = session.length

    length = record.length

    title_text = f'{BOLD}{record.title}{UNBOLD}'
    length_text = f'{length // 60:02}:{length % 60:02}' if length != -1 else f'no length'
    print(f'{title_text} | {id_text} | {length_text} | {index_text}{RESETCOLOR}')

    if video_exists:
        print(f'{UNDERLINE}Video | itag {record.video_stream} | "{record.video}"{UNUNDERLINE}')
    else:
        print(f'{UNDERLINE}No video found{UNUNDERLINE}')
    if audio_exists:
        print(f'{UNDERLINE}Audio | itag {record.audio_stream} | "{record.audio}"{UNUNDERLINE}')
    else:
        print(f'{UNDERLINE}No audio found{UNUNDERLINE}')

    print(record)

    if auto_video or auto_audio:
        get_video = auto_video
        get_audio = auto_audio
    else:
        if not video_exists:
            get_video = input_choice(['y', 'n'], lambda x: x.lower(), 'Video [Y]es or [N]o: ') == 'y'
        else:
            get_video = False
        if not audio_exists:
            get_audio = input_choice(['y', 'n'], lambda x: x.lower(), 'Audio [Y]es or [N]o: ') == 'y'
        else:
            get_audio = False

    if video_exists and audio_exists:
        print('Video and Audio already downloaded, nothing to do')
        return

    if not get_video and not get_audio:
        print('Every request was rejected, nothing to do')
        return

    print()
    if session.age_restricted:
        print(
            f'{RED}Video is age restricted and cannot be downloaded with this application (no authentication option){RESETCOLOR}')
        return

    if not os.path.exists(VIDEO_DIR): os.mkdir(VIDEO_DIR)
    if not os.path.exists(TRACK_DIR): os.mkdir(TRACK_DIR)

    all_streams = session.streams

    if get_video and not video_exists:  # Requested video
        video_updated = True
        video_streams = all_streams.filter(type='video')
        sorted_streams = sorted([stream for stream in video_streams if stream._filesize != 0],
                                key=lambda s: int(s.resolution[:len(s.resolution) - 1]), reverse=True)
        video_stream = sorted_streams[0]
        record.progressive = stream_is_progressive(video_stream)

        print(f'Video stream {video_stream}')
        if record.progressive:  # Video has both visual and audial
            print(f'Video is progressive, getting video')
            base_video_path = process_video_stream(video_stream, video_progressive)
            record.video = base_video_path
            record.video_stream = video_stream.itag
        else:  # Video is interlaced
            print(f'Video is interlaced')
            print(f'Downloading video')
            base_video_path = process_video_stream(video_stream, video_progressive)
            audio_updated = True
            if not audio_exists:  # If no audio, download
                print(f'Downloading audio')
                audio_streams = all_streams.filter(type='audio').order_by('abr').desc()
                audio_stream = audio_streams[0]
                print(f'Audio stream {audio_stream}')
                record.audio = process_audio_stream(audio_stream)
                record.audio_stream = audio_stream.itag
                audio_exists = True
            else:  # If audio exists, use existing
                print(f'Found existing audio')
                record.audio = records[video_id]['audio']
            record.video = merge_video_audio(base_video_path, audio_path)
            record.video_stream = video_stream.itag

    if get_audio and not audio_exists:  # Requested audio
        audio_updated = True
        if video_exists:  # If video exists, take audio from it
            print(f'Getting audio from video')
            record.audio = process_audio_from_video(video_path)
        else:  # If no video, download individually
            print(f'Downloading audio')
            audio_streams = all_streams.filter(type='audio').order_by('abr').desc()
            audio_stream = audio_streams[0]
            print(f'Audio stream {audio_stream}')
            record.audio = process_audio_stream(audio_stream)
            record.audio_stream = audio_stream.itag

    if video_id not in records:
        records[video_id] = record

        new_content = record.Parse()
        with open(RECORDS_FILE, 'a', encoding='utf-8') as f:
            f.write(new_content)
    elif video_updated or audio_updated:
        record = records[video_id]

        update_records()


def process_video_stream(video_stream: pytube.Stream, progressive: bool):
    video_at = video_stream.download(TEMP_VIDEO_DIR)
    video_file = os.path.basename(video_at)
    video_filename, video_ext = os.path.splitext(video_file)
    if not progressive:
        return video_at

    video_path = f'{VIDEO_DIR}{video_filename}.mp4'
    ffmpeg = ffmpy.FFmpeg(inputs={video_at: None},
                          outputs={video_path: None},
                          global_options='-y -loglevel warning')
    ffmpeg.run()
    os.remove(video_at)
    return video_path


def process_audio_from_video(video_path: str):
    video_file = os.path.basename(video_path)
    video_filename, _ = os.path.splitext(video_file)
    audio_path = f'{TRACK_DIR}{video_filename}.mp3'

    ffmpeg = ffmpy.FFmpeg(inputs={video_path: None},
                          outputs={audio_path: None},
                          global_options='-y -loglevel warning')
    ffmpeg.run()
    return audio_path


def process_audio_stream(audio_stream: pytube.Stream):
    audio_at = audio_stream.download(TEMP_TRACK_DIR)
    audio_file = os.path.basename(audio_at)
    audio_filename, _ = os.path.splitext(audio_file)
    audio_path = f'{TRACK_DIR}{audio_filename}.mp3'

    ffmpeg = ffmpy.FFmpeg(inputs={audio_at: None},
                          outputs={audio_path: None},
                          global_options='-y -loglevel warning')
    ffmpeg.run()
    os.remove(audio_at)
    return audio_path


def merge_video_audio(video_path: str, audio_path: str):
    video_file = os.path.basename(video_path)
    video_filename, _ = os.path.splitext(video_file)
    new_video_path = f'{VIDEO_DIR}{video_filename}.mp4'

    ffmpeg = ffmpy.FFmpeg(inputs={video_path: None, audio_path: None},
                          outputs={new_video_path: '-c copy -map 0:v:0 -map 1:a:0'},
                          global_options='-y -loglevel warning')
    ffmpeg.run()
    os.remove(video_path)
    return new_video_path


def Initialize():
    os.system('')
    cleanup_temp()

    if not os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            f.write('')

    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    containers = [[attr.split('=') for attr in container.splitlines() if attr] for container in content.split(RECORD_SEPERATOR)]
    print(containers)

    for container in containers:
        record = Record()
        if not container: continue  # (Skip empty records/attribute groups)
        for key, value in container:
            if key not in ALLOWED_KEYS: continue
            if value == 'None': value = None
            elif value == 'False': value = False
            elif value == 'True': value = True
            elif key == 'length' and value is not None: value = int(value)
            setattr(record, key, value)
        records[record.video_id] = record

    print(f'Loaded {len(records)} record/s')


def main():
    Initialize()

    while True:
        print('|Select the object to process| [V]ideo| [P]laylist (not working yet)| [R]epair'.replace('|', '\n'))
        user_choice = input('> ').lower()

        if not user_choice:
            continue

        print()
        first_char = user_choice[0]
        if first_char in 'v':
            print(f'Enter video url or id')
            video_string = input('> ')

            print()
            process_video(video_string)
        elif first_char in 'p':
            print('Enter url')
            playlist_string = input('> ')

            print()
            for url in pytube.Playlist(url=playlist_string):
                process_video(url, False, True)
        elif first_char in 'r':
            for video_id in records:
                record = records[video_id]

                get_video = record.video and not os.path.exists(record.video)
                get_audio = record.audio and not os.path.exists(record.audio)
                if get_video or get_audio:
                    process_video(video_id, get_video, get_audio)
        else:
            print('Selection not found')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
