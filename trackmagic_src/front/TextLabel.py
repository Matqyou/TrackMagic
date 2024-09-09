from front.DynamicRectangle import DynamicRectangle
from static.Numbers import Numbers
import pygame


class SelfAlign:
    LEFT = 0
    TOP = 0
    CENTER = 1
    RIGHT = 2
    BOTTOM = 2


class TextLabel(DynamicRectangle):
    def __init__(self, parent, font: pygame.font.Font, text: str = 'Text label', color=(255, 255, 255), fixed_size: tuple = (None, None), align_x: int = SelfAlign.LEFT, align_y: int = SelfAlign.TOP, name: str = None):
        super().__init__(parent, color=color, fixed_size=fixed_size, name=name)
        self.font = font
        self.text = text
        self.align_x = align_x
        self.align_y = align_y

        self.surface: pygame.Surface = None  # type: ignore
        self.label_surface: pygame.Surface = None  # type: ignore

        self.update_label()

    def update_label(self) -> None:
        self.label_surface = self.font.render(self.text, True, self.color)

    def update_surface(self) -> None:  # todo: text_label is bigger than the parent if there is any padding
        self.surface = pygame.Surface((Numbers.clamp_bottom(self.width, 0), Numbers.clamp_bottom(self.height, 0)), pygame.SRCALPHA)
        width, height = self.label_surface.get_size()

        if self.align_x == SelfAlign.LEFT:
            x = 0
        elif self.align_x == SelfAlign.CENTER:
            x = (self.width - width) / 2
        elif self.align_x == SelfAlign.RIGHT:
            x = self.width - width
        else:
            raise Exception()

        if self.align_y == SelfAlign.TOP:
            y = 0
        elif self.align_y == SelfAlign.CENTER:
            y = (self.height - height) / 2
        elif self.align_y == SelfAlign.BOTTOM:
            y = self.height - height
        else:
            raise Exception()

        self.surface.blit(self.label_surface, (x, y))

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
