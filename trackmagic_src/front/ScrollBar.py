from front.DynamicRectangle import DynamicRectangle
from front.ItemList import ItemList
import pygame


class ScrollBar(DynamicRectangle):
    def __init__(self, parent, item_list: ItemList, color=None, border=None, inner_color=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)
        self.item_list = item_list
        self.inner_color = inner_color

        self.progress: float = 0
        self.slider_spacing: int = 3
        self.slider_spacing2 = self.slider_spacing * 2
        self.slider_x: int = None  # type: ignore
        self.slider_y: int = None  # type: ignore
        self.slider_width: int = None  # type: ignore
        self.slider_height: int = None  # type: ignore

        self.item_list.set_progress(self.progress)

    def update_slider(self) -> None:
        if self.item_list:
            length = self.item_list.get_length()
            if self.align_vertically:
                rail_height = (self.height - self.slider_spacing2)
                self.slider_height = rail_height ** 2 / length
                self.slider_y = self.y + self.slider_spacing + (rail_height - self.slider_height) * self.progress

        self.slider_x = self.x + self.slider_spacing
        self.slider_width = self.width - self.slider_spacing2

    def update_children(self) -> None:
        self.update_slider()
        super().update_children()

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
            pygame.draw.rect(surface, self.inner_color, (self.slider_x, self.slider_y, self.slider_width, self.slider_height))

        for child in self.children:
            child.draw(surface, offset)
