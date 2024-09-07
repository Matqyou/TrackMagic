from PIL import Image
import os


class ImageProcessing:
    @staticmethod
    def convert_to_jpg(image_path: str) -> str:
        image_file = os.path.basename(image_path)
        image_filename, image_extension = os.path.splitext(image_file)

        if image_filename == '.jpg':
            return image_path

        converted_path = os.path.join(os.path.dirname(image_path), f'{image_filename}.jpg')
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')  # just for safety
            rgb_img.save(converted_path)
        return converted_path
