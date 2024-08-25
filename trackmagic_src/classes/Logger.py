from datetime import datetime
from time import time
import traceback
import os

LOGS_DIRECTORY = '../logs/'


class Logger:
    log_file_extension = 'txt'

    def __init__(self, log_file_name: str, log_to_file: bool = False):
        self.log_file_name: str = Logger.rename_file_if_exists(log_file_name, Logger.log_file_extension)
        self.log_to_file: bool = log_to_file

    def set_log_to_file(self, state: bool) -> None:
        self.log_to_file = state

    def run(self, func) -> None:
        try:
            func()
        except Exception as e:
            error_string = traceback.format_exc()
            self.log('ERROR', f'An error has occurred: {e}\nLog written to {self.log_file_name}\n{error_string}')
        except KeyboardInterrupt:
            self.log('EXIT', 'Closed via keyboard interrupt')

    def log(self, subsection: str = 'NORMAL', text: str = '') -> None:
        log_text = f'[{datetime.now().strftime("%m/%d/%Y %H:%M:%S")}][{subsection}] {text}\n'
        print(log_text, end='')

        if self.log_to_file:
            if not os.path.exists(LOGS_DIRECTORY):
                os.mkdir(LOGS_DIRECTORY)
            with open(f'{LOGS_DIRECTORY}{self.log_file_name}', 'a', encoding='utf-8') as log_file:
                log_file.write(log_text)

    @staticmethod
    def rename_file_if_exists(file_name: str, file_extension: str) -> str:
        file_number = 0
        search_file = '.'.join([file_name, file_extension])
        while os.path.exists(search_file):
            file_number += 1
            search_file = f'{file_name} {file_number}{file_extension}'
        return search_file


class Launcher:
    def __init__(self):
        self.startup_date_timestamp: datetime = datetime.now()
        self.startup_timestamp: float = time()

        self.startup_timestamp_int: int = int(self.startup_timestamp)
        self.logger = Logger(f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}')

    def launch(self, launch_main) -> None:
        self.logger.run(launch_main)
