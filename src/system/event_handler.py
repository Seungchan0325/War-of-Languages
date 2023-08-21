from collections import defaultdict

import pygame

from common import SingletonInstane


class EventHandler(SingletonInstane):

    def __init__(self):
        self._is_quit = False

        self._is_mouse_updated = False

        self._is_mouse_up = defaultdict(bool)
        self._is_mouse_down = defaultdict(bool)
        self._is_mouse_pressing = defaultdict(bool)

        self._is_key_updated = False

        self._is_key_up = defaultdict(bool)
        self._is_key_down = defaultdict(bool)
        self._is_key_pressing = defaultdict(bool)

    def init(self):
        pass

    def update(self):
        self._is_mouse_updated = False

        self._is_mouse_up.clear()
        self._is_mouse_down.clear()

        self._is_key_updated = False

        self._is_key_up.clear()
        self._is_key_down.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_quit = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self._is_mouse_updated = True
                self._is_mouse_up[event.button] = True
                self._is_mouse_pressing[event.button] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._is_mouse_updated = True
                self._is_mouse_down[event.button] = True
                self._is_mouse_pressing[event.button] = True

            elif event.type == pygame.KEYUP:
                self._is_key_updated = True
                self._is_key_up[event.key] = True
                self._is_key_pressing[event.key] = False

            elif event.type == pygame.KEYDOWN:
                self._is_key_updated = True
                self._is_key_down[event.key] = True
                self._is_key_pressing[event.key] = True

    @property
    def is_quit(self) -> bool:
        return self._is_quit

    @property
    def is_mouse_updated(self) -> bool:
        return self._is_mouse_updated

    @property
    def is_mouse_up(self) -> defaultdict:
        return self._is_mouse_up

    @property
    def is_mouse_down(self) -> defaultdict:
        return self._is_mouse_down

    @property
    def is_mouse_pressing(self) -> defaultdict:
        return self._is_mouse_pressing

    @property
    def is_key_updated(self) -> bool:
        return self._is_key_updated

    @property
    def is_key_up(self) -> defaultdict:
        return self._is_key_up

    @property
    def is_key_down(self) -> defaultdict:
        return self._is_key_down

    @property
    def is_key_pressing(self) -> defaultdict:
        return self._is_key_pressing
