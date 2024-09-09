from front.DynamicRectangle import DynamicRectangle
import pygame


class ScrollBar(DynamicRectangle):
    def __init__(self, parent, color=None, border=None, inner_color=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)

        self.inner_color = inner_color

    def draw(self, surface: pygame.Surface, offset: tuple = None) -> None:
        if offset is None:
            x, y = self.x, self.y
        else:
            offset_x, offset_y = offset
            x = self.x - offset_x
            y = self.y - offset_y

        if self.color is not None:
            pygame.draw.rect(surface, self.color, (x, y, self.width, self.height))

        if self.border is not None:
            pygame.draw.rect(surface, self.border, (x, y, self.width, self.height), 1)

        if self.inner_color is not None:
            pygame.draw.rect(surface, self.inner_color, ())

        for child in self.children:
            child.draw(surface, offset)
