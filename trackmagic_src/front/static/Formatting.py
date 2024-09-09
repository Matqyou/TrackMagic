class Formatting:
    @staticmethod
    def time_format(length: int) -> str:
        hours = length // 3600
        minutes = (length // 60) % 60
        seconds = length % 60

        if hours > 0:
            return f'{hours}:{minutes:0>2}:{seconds:0>2}'
        elif minutes > 0:
            return f'{minutes}:{seconds:0>2}'
        return f'{seconds}'

