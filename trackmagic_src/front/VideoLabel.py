from front.ImageLabel import ImageLabel
from front.static.Formatting import Formatting
import pygame


class VideoLabel(ImageLabel):
    def __init__(self, parent, font: pygame.font.Font, image: pygame.Surface, label: str = 'label', color=None, border=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, image=image, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)
        self.font = font
        self.label = label

    def update_surface(self) -> None:
        super().update_surface()
        length_surface = self.font.render(self.label, True, (255, 255, 255))
        length_width, length_height = length_surface.get_size()
        overlay = pygame.Surface((length_width + 4, length_height + 4))
        overlay.set_alpha(123)
        self.surface.blit(overlay, (self.width - overlay.get_width() - 2, self.height - overlay.get_height() - 2))
        self.surface.blit(length_surface, (self.width - length_width - 4, self.height - length_height - 4))


