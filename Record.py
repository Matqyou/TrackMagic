RECORD_SEPERATOR = '-= End of record =-\n'


class Record:
    def __init__(self):
        self.video_id = None
        self.title = None
        self.length = -1
        self.progressive = None
        self.video = None
        self.video_stream = None
        self.audio = None
        self.audio_stream = None

    def Parse(self):
        return '\n'.join(f'{i[0]}={i[1]}' for i in self.__dict__.items()) + '\n' + RECORD_SEPERATOR

    def __repr__(self):
        return str(self.__dict__)
