import pygame

from common import SingletonInstane
from game_config import GameConfig


class Screen(SingletonInstane):

    def __init__(self):
        self._screen_size: pygame.Rect
        self._screen: pygame.Surface

    def init(self):
        self._screen_size = pygame.Rect((0, 0), pygame.display.get_desktop_sizes()[0])
        self._screen = pygame.display.set_mode(self._screen_size.size, flags=pygame.FULLSCREEN)

        caption = GameConfig.instance().name
        pygame.display.set_caption(caption)

    def render(self, background: pygame.Surface, sprites: pygame.sprite.LayeredDirty):
        updates = sprites.draw(self._screen, background)
        pygame.display.update(updates)

    @property
    def area(self) -> pygame.Rect:
        return self._screen_size

    @property
    def size(self) -> tuple[int, int]:
        return self._screen_size.size

    @property
    def width(self) -> int:
        return self._screen_size.width

    @property
    def height(self) -> int:
        return self._screen_size.height
