import platform

import pygame

from common import get_monitor_size, SingletonInstane


class Screen(SingletonInstane):

    def __init__(self):
        self._screen_size = None
        self._screen = None

    def init(self):
        self._screen_size = (1920, 1080)
        if platform.system() == "Windows":
            self._screen_size = get_monitor_size()
        self._screen = pygame.display.set_mode(self._screen_size, pygame.FULLSCREEN)

    def render(self, sprites: pygame.sprite.LayeredDirty):
        updates = sprites.draw(self._screen)
        pygame.display.update(updates)

    @property
    def screen_size(self) -> pygame.Rect:
        return self._screen_size
