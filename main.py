""" Youtube maximum quality downloader application.
Supports individual links to videos and playlists.

Downloads videos with highest quality possible and
 saves a seperate audio file with it.

Dependencies:
 - pytube used to download YouTube streams. (pip install pytube)
 - FFmpeg used to convert and merge streams.

Made by Mαtq#0035 on Discord
User ID 243713302750953482 on https://discord.id/ & https://lookup.guru/
"""

import pytube
import ffmpy
import os
records = {}
RECORDS_FILE = 'records'
RECORD_SEPERATOR = '-= End of record =-\n'
VIDEO_DIR = 'Videos\\'
TRACK_DIR = 'Audio\\'
TEMP_DIR = 'Temp\\'
TEMP_VIDEO_DIR = TEMP_DIR + 'Video\\'
TEMP_TRACK_DIR = TEMP_DIR + 'Audio\\'
os.system('')
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
                os.remove(subdir+file)
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
        new_content += parse_record(record)

    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)


def parse_record(record: dict):
    parsed = ''
    for key, value in record.items():
        parsed += f'{key}={value}\n'
    parsed += RECORD_SEPERATOR
    return parsed


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


def process_video(video_string: str, auto_video = False, auto_audio = False):
    try: session = pytube.YouTube(url=video_string)
    except:
        try: session = pytube.YouTube(url=f'https://www.youtube.com/watch?v={video_string}')
        except: print('Invalid video string supplied'); return

    video_id = session.video_id
    id_text = f'{UNDERLINE}{video_id}{UNUNDERLINE}'

    video_updated = False
    video_exists = False
    audio_updated = False
    audio_exists = False

    if video_id in records:  # Existing record
        index_text = f'Loaded #{list(records).index(video_id)}'
        record = records[video_id]

        title = record['title']
        length = int(record['length'])
        video_progressive = record['progressive']
        video_path = record['video']
        video_itag = record['video_stream']
        audio_path = record['audio']
        audio_itag = record['audio_stream']

        video_exists = 'video' in record and record['video'] is not None
        audio_exists = 'audio' in record and record['audio'] is not None

        if video_exists and not os.path.exists(video_path):
            video_exists = False
            print('Video has been lost...')
        if audio_exists and not os.path.exists(audio_path):
            audio_exists = False
            print('Audio has been lost...')
    else:  # New record
        index_text = f'Created #{len(records)}'
        title = session.title
        length = session.length
        video_progressive = None
        video_path = None
        video_itag = None
        audio_path = None
        audio_itag = None


    title_text = f'{BOLD}{title}{UNBOLD}'
    length_text = f'{length//60:02}:{length%60:02}'
    print(f'{title_text} | {id_text} | {length_text} | {index_text}{RESETCOLOR}')

    if video_exists: print(f'{UNDERLINE}Video | itag {video_itag} | "{video_path}"{UNUNDERLINE}')
    else: print(f'{UNDERLINE}No video found{UNUNDERLINE}')
    if audio_exists: print(f'{UNDERLINE}Audio | itag {audio_itag} | "{audio_path}"{UNUNDERLINE}')
    else: print(f'{UNDERLINE}No audio found{UNUNDERLINE}')

    if auto_video or auto_audio:
        get_video = auto_video
        get_audio = auto_audio
    else:
        if not video_exists: get_video = input_choice(['y', 'n'], lambda x: x.lower(), 'Video [Y]es or [N]o: ') == 'y'
        else: get_video = False
        if not audio_exists: get_audio = input_choice(['y', 'n'], lambda x: x.lower(), 'Audio [Y]es or [N]o: ') == 'y'
        else: get_audio = False

    if video_exists and audio_exists:
        print('Video and Audio already downloaded, nothing to do')
        return

    if not get_video and not get_audio:
        print('Every request was rejected, nothing to do')
        return

    print()
    if session.age_restricted:
        print(f'{RED}Video is age restricted and cannot be downloaded with this application (no authentication option){RESETCOLOR}')
        return

    if not os.path.exists(VIDEO_DIR): os.mkdir(VIDEO_DIR)
    if not os.path.exists(TRACK_DIR): os.mkdir(TRACK_DIR)

    all_streams = session.streams

    if get_video and not video_exists:  # Requested video
        video_updated = True
        video_streams = all_streams.filter(type='video')
        sorted_streams = sorted([stream for stream in video_streams if stream._filesize != 0], key=lambda s: int(s.resolution[:len(s.resolution) - 1]), reverse=True)
        video_stream = sorted_streams[0]
        video_progressive = stream_is_progressive(video_stream)

        print(f'Video stream {video_stream}')
        if video_progressive:  # Video has both visual and audial
            print(f'Video is progressive, getting video')
            base_video_path = process_video_stream(video_stream, video_progressive)
            video_path = base_video_path
            video_itag = video_stream.itag
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
                audio_path = process_audio_stream(audio_stream)
                audio_itag = audio_stream.itag
                audio_exists = True
            else:  # If audio exists, use existing
                print(f'Found existing audio')
                audio_path = records[video_id]['audio']
            video_path = merge_video_audio(base_video_path, audio_path)
            video_itag = video_stream.itag

    if get_audio and not audio_exists:  # Requested audio
        audio_updated = True
        if video_exists:  # If video exists, take audio from it
            print(f'Getting audio from video')
            audio_path = process_audio_from_video(video_path)
        else:  # If no video, download individually
            print(f'Downloading audio')
            audio_streams = all_streams.filter(type='audio').order_by('abr').desc()
            audio_stream = audio_streams[0]
            print(f'Audio stream {audio_stream}')
            audio_path = process_audio_stream(audio_stream)
            audio_itag = audio_stream.itag

    if video_id not in records:
        records[video_id] = {}
        record = records[video_id]
        record['video_id'] = video_id
        record['title'] = title
        record['length'] = length
        record['progressive'] = video_progressive
        record['video'] = video_path
        record['video_stream'] = video_itag
        record['audio'] = audio_path
        record['audio_stream'] = audio_itag

        new_content = parse_record(record)
        with open(RECORDS_FILE, 'a', encoding='utf-8') as f:
            f.write(new_content)
    elif video_updated or audio_updated:
        record = records[video_id]

        if video_updated:
            record['video'] = video_path
            record['video_stream'] = video_itag
            record['progressive'] = video_progressive

        if audio_updated:
            record['audio'] = audio_path
            record['audio_stream'] = audio_itag

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


forms = {'v': 'video'}


def main():
    os.system('')
    cleanup_temp()

    if not os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            f.write('')

    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    containers = [[attr for attr in container.splitlines() if attr] for container in content.split(RECORD_SEPERATOR)]
    for container in containers:
        result = {}
        for attribute in container:
            seperate_at = attribute.find('=')
            key = attribute[:seperate_at]
            value = attribute[seperate_at + 1:]
            if value == 'None':
                value = None
            elif value == 'False':
                value = False
            elif value == 'True':
                value = True
            result[key] = value
        if 'video_id' in result:
            video_id = result['video_id']
            records[video_id] = result
    print(f'Loaded {len(records)} record/s')

    while True:
        print('|Select the object to process| [V]ideo| [P]laylist (not working yet)| [R]epair'.replace('|', '\n'))
        user_choice = input('> ').lower()

        if not user_choice:
            continue

        print()
        first_char = user_choice[0]
        if first_char in 'v':
            form_name = forms[first_char]
            print(f'Enter {form_name} url or id')
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
                video_path = records[video_id]['video']
                audio_path = records[video_id]['audio']

                get_video = video_path and not os.path.exists(video_path)
                get_audio = audio_path and not os.path.exists(audio_path)
                if get_video or get_audio:
                    process_video(video_id, get_video, get_audio)
        else:
            print('Selection not found')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
