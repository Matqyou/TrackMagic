from back.static.Configuration import Configuration
import pygetwindow as gw
import shutil
import os


class FileExplorer:
    @staticmethod
    def sanitize_filename(filename: str):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    @staticmethod
    def remove_file(filepath: str):
        os.remove(filepath)

    @staticmethod
    def move_file(source_filepath: str, destination_filepath: str) -> str:
        return shutil.move(source_filepath, destination_filepath)

    @staticmethod
    def move_to_folder(source_filepath: str, destination_folder: str, rename_to_path_filename: str = None) -> str:
        if not os.path.exists(destination_folder):
            os.mkdir(destination_folder)

        if rename_to_path_filename:
            file: str = os.path.basename(rename_to_path_filename)
            _, source_extension = os.path.splitext(source_filepath)
            rename_filename, _ = os.path.splitext(file)
            filename: str = f'{rename_filename}{source_extension}'
        else:
            filename: str = os.path.basename(source_filepath)
        destination_filepath: str = os.path.join(destination_folder, filename)
        return shutil.move(source_filepath, destination_filepath)

    @staticmethod
    def rename_base(file_path: str, new_name: str) -> str:
        file_dir = os.path.dirname(file_path)
        _, extension = os.path.splitext(file_path)
        new_filepath = os.path.join(file_dir, f'{new_name}{extension}')
        os.rename(file_path, new_filepath)
        return new_filepath

    @staticmethod
    def create_folder(folder_path: str) -> None:
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    @staticmethod
    def is_folder_open(folder_path: str):
        folder_path = os.path.abspath(folder_path)
        folder_name = os.path.basename(folder_path)
        for window in gw.getWindowsWithTitle(folder_name):
            if folder_path in window.title:
                return True
        return False

    @staticmethod
    def open_folder_in_explorer(folder_path):
        try:
            if not FileExplorer.is_folder_open(folder_path):
                os.startfile(os.path.abspath(folder_path))
            else:
                print(f"Folder '{folder_path}' is already open.")
        except Exception as e:
            print("Error:", e)

    @staticmethod
    def cleanup_temp():
        path = f'{os.getcwd()}\\{Configuration.temp_dir}'
        if os.path.exists(path):
            for file in os.listdir(path):
                os.remove(path+file)
            os.rmdir(path)

    # @staticmethod
    # def update_records():
    #     new_content = ''
    #     for record in gRecords.values():
    #         new_content += record.Parse()
    #
    #     with open(Configuration.records_file, 'w', encoding='utf-8') as f:
    #         f.write(new_content)

    @staticmethod
    def read_or_create_empty(filepath: str) -> str:
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8'):
                pass

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
