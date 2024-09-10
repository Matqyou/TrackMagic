from front.DynamicRectangle import DynamicRectangle
from static.Numbers import Numbers
import pygame


class ItemList(DynamicRectangle):
    def __init__(self, parent, color=None, border=None, fixed_size: tuple = (None, None), padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        super().__init__(parent, color=color, border=border, fixed_size=fixed_size, padding=padding, align_vertically=align_vertically, spacing=spacing, name=name)

        self.surface: pygame.Surface = None  # type: ignore
        self.total_width: int = None  # type: ignore
        self.total_height: int = None  # type: ignore
        self.length_offset: float = 0
        self.last_length_offset: float = 0

    def get_length(self) -> int:
        return (self.total_width, self.total_height)[self.align_vertically]

    def set_progress(self, new_progress: float) -> None:
        self.length_offset = (self.total_height - self.height) * new_progress
        if self.length_offset != self.last_length_offset:
            self.last_length_offset = self.length_offset
            self.update_children()

    def add_child(self, child) -> None:
        super().add_child(child)

        num_children = len(self.children)
        if num_children == 0:
            self.total_height = 0
            return

        fixed_width = 0
        fixed_height = 0
        for child in self.children:
            if child.fixed_width is not None:
                fixed_width += child.fixed_width
            if child.fixed_height is not None:
                fixed_height += child.fixed_height

        total_spacing = self.spacing * (num_children - 1)
        self.total_height = fixed_height + total_spacing
        self.total_width = fixed_width + total_spacing

    def update_surface(self) -> None:
        width = Numbers.clamp_bottom(self.width - self.padding_x2, 0)
        height = Numbers.clamp_bottom(self.height - self.padding_y2, 0)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def update_children(self) -> None:
        self.update_surface()

        num_children = len(self.children)
        if num_children == 0:
            return

        fixed_width = 0
        fixed_height = 0
        num_dynamic_width = 0
        num_dynamic_height = 0
        for child in self.children:
            if child.fixed_width is not None:
                fixed_width += child.fixed_width
            else:
                num_dynamic_width += 1
            if child.fixed_height is not None:
                fixed_height += child.fixed_height
            else:
                num_dynamic_height += 1

        total_spacing = self.spacing * (num_children - 1)

        current_x = self.padding_x
        current_y = self.padding_y
        if self.align_vertically:
            single_height = None
            if num_dynamic_height != 0:
                dynamic_height = self.height - fixed_height - total_spacing - self.padding_y2
                single_height = dynamic_height / num_dynamic_height
            full_width = self.width - self.padding_x2
            for child in self.children:
                child.x = self.x + current_x
                child.y = self.y + current_y - self.length_offset
                child.width = full_width
                if child.fixed_height is not None:
                    child.height = child.fixed_height
                else:
                    child.height = single_height
                current_y += child.height + self.spacing
                child.update_children()
        else:  # not self.align_vertically
            single_width = None
            if num_dynamic_width != 0:
                dynamic_width = self.width - fixed_width - total_spacing - self.padding_x2
                single_width = dynamic_width / num_dynamic_width
            full_height = self.height - self.padding_y2
            for child in self.children:
                child.x = self.x + current_x - self.length_offset
                child.y = self.y + current_y
                child.height = full_height
                if child.fixed_width is not None:
                    child.width = child.fixed_width
                else:
                    child.width = single_width
                current_x += child.width + self.spacing
                child.update_children()

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
            pygame.draw.rect(self.surface, self.color, (x, y, self.width, self.height))

        if self.border is not None:
            pygame.draw.rect(self.surface, self.border, (x, y, self.width, self.height), 1)

        for child in self.children:
            child.draw(self.surface, (padded_x, padded_y))
        surface.blit(self.surface, (padded_x, padded_y))
