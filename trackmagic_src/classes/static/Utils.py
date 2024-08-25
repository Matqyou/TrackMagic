import re


class Utils:
    @staticmethod
    def none_to_zero(value):
        if value is None:
            return 0
        return value

    @staticmethod
    def get_video_id_from_url(video_url: str) -> str:
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, video_url)
        return match.group(1) if match else None
