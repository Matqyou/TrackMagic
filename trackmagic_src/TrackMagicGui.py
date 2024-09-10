from front.StationaryRectangle import StationaryRectangle
from front.DynamicRectangle import DynamicRectangle
from front.TextLabel import TextLabel, SelfAlign
from front.static.Formatting import Formatting
from front.ImageLabel import ImageLabel
from front.VideoLabel import VideoLabel
from front.ScrollBar import ScrollBar
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
        self.screen = pygame.display.set_mode((720, 720), pygame.RESIZABLE | pygame.HIDDEN)
        self.width, self.height = self.screen.get_size()

    def main(self) -> None:
        font = pygame.font.Font(os.path.join(Configuration.assets_dir, 'arial-unicode-ms.ttf'), 16)
        font_small = pygame.font.Font(os.path.join(Configuration.assets_dir, 'arial-unicode-ms.ttf'), 14)
        font_smallest = pygame.font.Font(os.path.join(Configuration.assets_dir, 'Roboto-Bold.ttf'), 10)

        screen = StationaryRectangle((0, 0, self.width, self.height), events=True, padding=(15, 15), name='screen')
        rectangle = DynamicRectangle(screen, events=True, color=0x000000, padding=(10, 10), spacing=5, name='rectangle')

        # navbar = DynamicRectangle(rectangle, color=0x333333, border=0x666666, fixed_size=(None, 60), padding=(5, 5), align_vertically=False, spacing=5, name='navbar')
        search = DynamicRectangle(rectangle, events=True, color=None, border=0x666666, fixed_size=(None, 50), padding=(5, 5), align_vertically=False, spacing=5, name='search_bar')
        search_bar = DynamicRectangle(search, events=True, color=(50, 50, 50), name='search')
        search_button = DynamicRectangle(search, events=True, color=(50, 50, 50), fixed_size=(50, None), name='search_button')
        results = DynamicRectangle(rectangle, events=True, color=(16, 16, 16), border=0x666666, padding=(5, 5), spacing=2, align_vertically=False, name='results')
        results_list = ItemList(results, events=True, color=(16, 16, 16), spacing=5, name='results')

        for playlist in self.trackmagic.playlists.playlists.values():
            thumbnail_surface = None
            if playlist.records and (first_record := playlist.records[0]) is not None:
                video_id, _ = first_record
                thumbnail_surface = pygame.image.load(self.trackmagic.storage.get_record(video_id).thumbnail)

            item = DynamicRectangle(results_list, events=True, color=None, fixed_size=(None, 80), padding=(5, 5), align_vertically=False, spacing=5)
            title = f'{playlist.name}'
            playlist_id = f'{playlist.playlist_id}'
            label = f'{playlist.num_media} items - {Formatting.time_format(playlist.total_length)}'

            thumbnail = VideoLabel(item, font_smallest, thumbnail_surface, label=label, fixed_size=(124, 70))
            right_part = DynamicRectangle(item)
            top_part = DynamicRectangle(right_part, fixed_size=(None, 25), align_vertically=False)
            bottom_part = DynamicRectangle(right_part, align_vertically=False)
            label = TextLabel(top_part, font, text=title, color=(255, 255, 255), align_y=SelfAlign.BOTTOM)
            label2 = TextLabel(bottom_part, font_small, text=playlist_id, color=(176, 176, 176), align_y=SelfAlign.TOP)
            # label3 = TextLabel(bottom_part, font_smallest, text=length, color=(255, 255, 255), fixed_size=(75, None), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)

        for record in self.trackmagic.storage.records.values():
            thumbnail_surface = None
            if record.thumbnail is not None:
                thumbnail_surface = pygame.image.load(record.thumbnail)

            item = DynamicRectangle(results_list, events=True, color=None, fixed_size=(None, 70), padding=(5, 5), align_vertically=False, spacing=5)
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

            thumbnail = VideoLabel(item, font_smallest, thumbnail_surface, label=length, fixed_size=(107, 60))
            right_part = DynamicRectangle(item)
            top_part = DynamicRectangle(right_part, fixed_size=(None, 25), align_vertically=False)
            bottom_part = DynamicRectangle(right_part, align_vertically=False)
            label = TextLabel(top_part, font, text=title, color=(255, 255, 255), align_y=SelfAlign.BOTTOM)
            label2 = TextLabel(bottom_part, font_small, text=media, color=(176, 176, 176), align_y=SelfAlign.TOP)
            # label3 = TextLabel(bottom_part, font_smallest, text=length, color=(255, 255, 255), fixed_size=(75, 0), align_x=SelfAlign.LEFT, align_y=SelfAlign.CENTER)

        results_bar = ScrollBar(results, results_list, events=True, slider_spacing=1, color=None, inner_color=0xABABAB, fixed_size=(10, None), name='results_bar')

        # title = DynamicRectangle(rectangle, color=0x111111, fixed_size=(None, 150), name='title')

        screen.update_children()
        self.screen = pygame.display.set_mode(self.screen.get_size(), pygame.RESIZABLE)

        running = True
        while running:
            for event in pygame.event.get():
                screen.event(event)
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
