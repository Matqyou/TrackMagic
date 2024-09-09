from back.static.Configuration import Configuration
from back.static.FileExplorer import FileExplorer
from back.Records import Records
from back.Logger import Logger
import datetime
import os


class Playlists:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.playlists: dict = {}

    def load_playlists(self, records: Records) -> None:
        content = FileExplorer.read_or_create_empty(Configuration.playlists_file)
        records_unparsed = [attributes for attributes in content.split(Configuration.playlist_seperator)]

        for attributes in records_unparsed:
            playlist = Playlist()
            if playlist.parse(attributes):
                playlist.get_metadata(records)
                self.playlists[playlist.playlist_id] = playlist

        self.logger.log('Playlists', f'Loaded {len(self.playlists)} playlist/s')

    def save_playlists(self) -> None:
        new_content = ''
        new_content += Playlist().get_playlist_parameters()
        for playlist in self.playlists.values():
            new_content += playlist.serialize()

        with open(Configuration.playlists_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

    def get_playlist(self, playlist_id: str):
        return self.playlists.get(playlist_id, None)

    def update_playlist(self, playlist):
        playlist_id: str = playlist.playlist_id
        self.playlists[playlist_id] = playlist


class Playlist:
    def __init__(self):
        self.playlist_id: str = None  # type: ignore
        self.name: str = None  # type: ignore
        self.records: list[str] = None  # type: ignore
        self.date_created: datetime.datetime = None  # type: ignore
        self.date_modified: datetime.datetime = None  # type: ignore
        self.num_media: int = None  # type: ignore
        self.total_length: int = None  # type: ignore
        self.total_filesize: int = None  # type: ignore

    def get_metadata(self, records: Records) -> None:
        self.num_media = 0
        self.total_length = 0
        self.total_filesize = 0
        for video_id, media_type in self.records:
            record = records.get_record(video_id)
            if record is None:
                continue

            self.num_media += 1
            if record.length is not None:
                self.total_length += record.length
            self.total_filesize += -1  # todo

    def get_playlist_parameters(self) -> str:
        return '# ' + ', '.join(self.__dict__.keys()) + '\n'

    def serialize(self) -> str:
        result = []
        for key, item in self.__dict__.items():
            if key == 'records':
                items = '|'.join('.'.join(record) for record in item)
                result.append(f'{key}={items}')
            else:
                result.append(f'{key}={item}')
        return '\n'.join(result) + '\n' + Configuration.playlist_seperator

    @staticmethod
    def _split_attributes(unparsed_attributes: list[str]) -> list[tuple]:
        result = []
        for attribute in unparsed_attributes:
            if not attribute or attribute[0] == '#':
                continue

            eq_at = attribute.find('=')
            if eq_at == -1:
                continue

            key = attribute[:eq_at]
            value = attribute[eq_at+1:]
            result.append((key, value))
        return result

    @staticmethod
    def _split_records(unparsed_records: list[str]) -> list[tuple]:
        return [tuple(record.split('.')) for record in unparsed_records]

    def parse(self, unparsed_attributes: str) -> bool:
        attributes = Playlist._split_attributes(unparsed_attributes.splitlines(keepends=False))

        if not attributes:
            return False  # Drop bad records (empty lines, corrupted, etc.)

        for key, value in attributes:
            if value == 'None':
                value = None
            elif value == 'False':
                value = False
            elif value == 'True':
                value = True
            elif key == 'records' and value is not None:
                value = Playlist._split_records(value.split('|'))
            elif key in ['num_media', 'total_length', 'total_filesize']:
                value = int(value)
            setattr(self, key, value)
        return True

    def __repr__(self):
        return str(self.__dict__)
