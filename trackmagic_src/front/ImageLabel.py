from front.DynamicRectangle import DynamicRectangle
from static.Numbers import Numbers
import pygame


class ImageLabel(DynamicRectangle):
    def __init__(self, parent, image: pygame.Surface, color=None, border=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)
        self.image = image

        self.last_scale: tuple = None  # type: ignore
        self.scaled: pygame.Surface = None  # type: ignore
        self.surface: pygame.Surface = None  # type: ignore

    def update_surface(self) -> None:
        self.surface = pygame.Surface((Numbers.clamp_bottom(self.width, 0), Numbers.clamp_bottom(self.height, 0)))

        if self.image is None:
            return

        width, height = self.surface.get_size()
        ratio = width / height

        image_width, image_height = self.image.get_size()
        image_ratio = image_width / image_height
        image_ratio2 = image_height / image_width

        if image_ratio > ratio:
            new_width = width
            new_height = image_ratio2 * width
            x = 0
            y = (height - new_height) / 2
        elif image_ratio < ratio:
            new_height = height
            new_width = image_ratio * height
            y = 0
            x = (width - new_width) / 2
        else:
            new_width = width
            new_height = height
            x, y = 0, 0

        if self.last_scale != (new_width, new_height):
            self.last_scale = new_width, new_height
            self.scaled = pygame.transform.smoothscale(self.image, self.last_scale)
        self.surface.blit(self.scaled, (x, y))

    def update_children(self) -> None:
        self.update_surface()
        super().update_children()

    def draw(self, surface: pygame.Surface, offset: tuple = None) -> None:
        if offset is None:
            x, y = self.x, self.y
        else:
            offset_x, offset_y = offset
            x = self.x - offset_x
            y = self.y - offset_y

        surface.blit(self.surface, (x, y))
