from front.DynamicRectangle import DynamicRectangle
from static.Numbers import Numbers
import pygame


class ItemList(DynamicRectangle):
    def __init__(self, parent, color=0x000000, border=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)
        self.surface: pygame.Surface = None  # type: ignore

    def update_surface(self) -> None:
        width = Numbers.clamp_bottom(self.width - self.padding_x2, 0)
        height = Numbers.clamp_bottom(self.height - self.padding_y2, 0)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

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
        padded_x = x + self.padding_x
        padded_y = y + self.padding_y

        if self.color is not None:
            pygame.draw.rect(surface, self.color, (x, y, self.width, self.height))

        if self.border is not None:
            pygame.draw.rect(surface, self.border, (x, y, self.width, self.height), 1)

        for child in self.children:
            child.draw(self.surface, (padded_x, padded_y))
        surface.blit(self.surface, (padded_x, padded_y))
