from classes.static.Configuration import Configuration
from classes.static.FileExplorer import FileExplorer
from classes.Logger import Logger
import os


class Records:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.records: dict = {}

    def check_integrity(self) -> None:
        for record in self.records.values():
            record.check_file_integrity()
        self.save_records()

    def load_records(self) -> None:
        content = FileExplorer.read_or_create_empty(Configuration.records_file)
        records_unparsed = [attributes for attributes in content.split(Configuration.record_seperator)]

        for attributes in records_unparsed:
            record = Record()
            if record.parse(attributes):
                self.records[record.video_id] = record

        self.logger.log('Records', f'Loaded {len(self.records)} record/s')

    def save_records(self) -> None:
        new_content = ''
        for record in self.records.values():
            new_content += record.serialize()

        with open(Configuration.records_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

    def get_record(self, video_id: str):
        return self.records.get(video_id, None)

    def update_record(self, record):
        video_id: str = record.video_id
        self.records[video_id] = record


class Record:
    def __init__(self):
        self.video_id: str = None  # type: ignore
        self.title: str = None  # type: ignore
        self.length: int = None  # type: ignore
        self.video: str = None  # type: ignore
        self.video_stream: str = None  # type: ignore
        self.audio: str = None  # type: ignore
        self.audio_stream: str = None  # type: ignore
        self.thumbnail: str = None  # type: ignore

    def check_file_integrity(self) -> bool:
        changed_data = False
        if self.video is not None and not os.path.exists(self.video):
            self.video = None
            self.video_stream = None
            changed_data = True

        if self.audio is not None and not os.path.exists(self.audio):
            self.audio = None
            self.audio_stream = None
            changed_data = True

        return changed_data

    def serialize(self) -> str:
        return '\n'.join(f'{key}={item}' for key, item in self.__dict__.items()) + '\n' + Configuration.record_seperator

    @staticmethod
    def _split_attributes(unparsed_attributes: list[str]) -> list[tuple]:
        result = []
        for attribute in unparsed_attributes:
            eq_at = attribute.find('=')
            key = attribute[:eq_at]
            value = attribute[eq_at+1:]
            result.append((key, value))
        return result

    def parse(self, unparsed_attributes: str) -> bool:
        attributes = Record._split_attributes(unparsed_attributes.splitlines(keepends=False))

        if not attributes:
            return False  # Drop bad records (empty lines, corrupted, etc.)

        for key, value in attributes:
            if value == 'None':
                value = None
            elif value == 'False':
                value = False
            elif value == 'True':
                value = True
            elif key == 'length' and value is not None:
                value = int(value)
            setattr(self, key, value)
        return True

    def __repr__(self):
        return str(self.__dict__)
