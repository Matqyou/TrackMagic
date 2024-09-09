from front.StationaryRectangle import StationaryRectangle
import pygame


class DynamicRectangle(StationaryRectangle):
    def __init__(self, parent, color=None, border=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__((parent.x, parent.y, 0, 0), color=color, border=border, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)
        self.parent = parent
        self.fixed_width, self.fixed_height = fixed_size

        self.parent.children.append(self)
