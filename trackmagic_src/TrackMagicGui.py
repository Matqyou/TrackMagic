from front.StationaryRectangle import StationaryRectangle
from front.DynamicRectangle import DynamicRectangle
from front.TextLabel import TextLabel, SelfAlign
from front.static.Formatting import Formatting
from front.ImageLabel import ImageLabel
from front.ItemList import ItemList
from TrackMagic import *
import pygame
import atexit
import os


class TrackMagicGui:
    def __init__(self, trackmagic: TrackMagic):
        self.trackmagic = trackmagic
        self.screen: pygame.Surface = None  # type: ignore
        self.width: int = None  # type: ignore
        self.height: int = None  # type: ignore

    def init(self) -> None:
        pygame.init()
        icon = pygame.image.load(os.path.join(Configuration.assets_dir, 'icon.png'))
        pygame.display.set_icon(icon)
        pygame.display.set_caption('TrackMagic')
        self.screen = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
        self.width, self.height = self.screen.get_size()

    def main(self) -> None:
        font = pygame.font.SysFont(os.path.join(Configuration.assets_dir, 'Roboto-Medium.ttf'), 30)

        screen = StationaryRectangle((0, 0, self.width, self.height), padding=(15, 15), name='screen')
        rectangle = DynamicRectangle(screen, color=0x000000, padding=(10, 10), spacing=5, name='rectangle')

        search_bar = DynamicRectangle(rectangle, color=0x333333, border=0x666666, fixed_size=(None, 60), padding=(5, 5), align_vertically=False, spacing=5, name='search_bar')
        search = DynamicRectangle(search_bar, color=0x666666, name='search')
        search_button = DynamicRectangle(search_bar, color=0x666666, fixed_size=(60, None), name='search_button')
        results = ItemList(rectangle, color=0x333333, border=0x666666, padding=(5, 5), spacing=5, name='results')

        for playlist in self.trackmagic.playlists.playlists.values():
            thumbnail_surface = None
            if playlist.records and (first_record := playlist.records[0]) is not None:
                video_id, _ = first_record
                thumbnail_surface = pygame.image.load(self.trackmagic.storage.get_record(video_id).thumbnail)

            item = DynamicRectangle(results, color=(85, 51, 51, 255), fixed_size=(None, 80), padding=(5, 5), align_vertically=False, spacing=5)
            title = f'{playlist.name}'
            items = f'{playlist.num_media} items'
            length = f'{Formatting.time_format(playlist.total_length)}'

            thumbnail = ImageLabel(item, thumbnail_surface, fixed_size=(124, 70))
            right_part = DynamicRectangle(item)
            top_part = DynamicRectangle(right_part, align_vertically=False)
            bottom_part = DynamicRectangle(right_part, align_vertically=False)
            label = TextLabel(top_part, font, text=title, color=(255, 255, 255), align_y=SelfAlign.CENTER)
            label2 = TextLabel(bottom_part, font, text=items, color=(255, 255, 255), fixed_size=(100, None), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)
            label3 = TextLabel(bottom_part, font, text=length, color=(255, 255, 255), fixed_size=(75, None), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)

        for record in self.trackmagic.storage.records.values():
            thumbnail_surface = None
            if record.thumbnail is not None:
                thumbnail_surface = pygame.image.load(record.thumbnail)

            item = DynamicRectangle(results, color=(85, 51, 51, 255), fixed_size=(None, 70), padding=(5, 5), align_vertically=False, spacing=5)
            title = f'{record.title}'
            if record.video and record.audio:
                media = 'Both'
            elif record.video:
                media = 'Video'
            elif record.audio:
                media = 'Audio'
            else:
                media = 'None'
            length = f'{Formatting.time_format(record.length)}'

            thumbnail = ImageLabel(item, thumbnail_surface, fixed_size=(107, 60))
            right_part = DynamicRectangle(item)
            top_part = DynamicRectangle(right_part, align_vertically=False)
            bottom_part = DynamicRectangle(right_part, align_vertically=False)
            label = TextLabel(top_part, font, text=title, color=(255, 255, 255), align_y=SelfAlign.CENTER)
            label2 = TextLabel(bottom_part, font, text=media, color=(255, 255, 255), fixed_size=(100, 0), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)
            label3 = TextLabel(bottom_part, font, text=length, color=(255, 255, 255), fixed_size=(75, 0), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)

        # title = DynamicRectangle(rectangle, color=0x111111, fixed_size=(None, 150), name='title')

        screen.update_children()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.display.set_caption('Shutting down..')
                elif event.type == pygame.VIDEORESIZE:
                    screen.width, screen.height = event.w, event.h
                    screen.update_children()

            self.screen.fill(0x440066)
            screen.draw(self.screen)
            pygame.display.update()


def main():
    trackmagic = TrackMagic()
    trackmagic.init()

    instance = TrackMagicGui(trackmagic)
    instance.init()
    instance.main()


def cleanup():
    FileExplorer.cleanup_temp()


if __name__ == '__main__':
    atexit.register(cleanup)
    main()
