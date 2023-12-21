class Stream:
    def __init__(self):
        self.pytube_stream = None

    def IsProgressive(self) -> bool:
        return self.pytube_stream.video_codec is not None \
           and self.pytube_stream.audio_codec is not None
