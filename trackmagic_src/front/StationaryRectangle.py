import pygame


class StationaryRectangle:
    def __init__(self, rect: tuple, events: bool = False, color=None, border=None, padding: tuple = None, align_vertically: bool = True, spacing: int = 0, name: str = None):
        self.x, self.y, self.width, self.height = rect
        self.right_x = self.x + self.width
        self.bottom_y = self.y + self.height
        self.events = events
        self.color = color
        self.border = border

        if padding is None:
            padding = 0, 0

        self.padding_x, self.padding_y = padding
        self.padding_x2 = self.padding_x * 2
        self.padding_y2 = self.padding_y * 2
        self.align_vertically = align_vertically
        self.spacing = spacing
        self.name = name

        self.children = []

    def add_child(self, child) -> None:
        self.children.append(child)

    def update_edges(self) -> None:  # todo: optimize
        self.right_x = self.x + self.width
        self.bottom_y = self.y + self.height

    def update_children(self) -> None:
        self.update_edges()

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
                child.y = self.y + current_y
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
                child.x = self.x + current_x
                child.y = self.y + current_y
                child.height = full_height
                if child.fixed_width is not None:
                    child.width = child.fixed_width
                else:
                    child.width = single_width
                current_x += child.width + self.spacing
                child.update_children()

    def event(self, event: pygame.event.Event) -> bool:
        if not self.events:
            return False

        for child in self.children:
            if child.event(event):
                return True
        return False

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

        for child in self.children:
            child.draw(surface, offset)
