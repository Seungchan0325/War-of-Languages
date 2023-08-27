from dataclasses import dataclass
from collections import defaultdict

import pygame

from common import SingletonInstane


@dataclass
class MouseEvent:
    is_updated = False
    is_up = defaultdict(bool)
    is_down = defaultdict(bool)
    is_pressing = defaultdict(bool)


@dataclass
class KeyEvent:
    is_updated = False
    is_up = defaultdict(bool)
    is_down = defaultdict(bool)
    is_pressing = defaultdict(bool)


class EventHandler(SingletonInstane):

    def __init__(self):
        self._is_quit: bool

        self._mouse_event: MouseEvent
        self._key_event: KeyEvent

    def init(self):
        self._is_quit = False
        self._mouse_event = MouseEvent()
        self._key_event = KeyEvent()

    # Update events
    def update(self):
        self._mouse_event.is_updated = False

        self._mouse_event.is_up.clear()
        self._mouse_event.is_down.clear()

        self._key_event.is_updated = False

        self._key_event.is_up.clear()
        self._key_event.is_down.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_quit = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_event.is_updated = True
                self._mouse_event.is_up[event.button] = True
                self._mouse_event.is_pressing[event.button] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_event.is_updated = True
                self._mouse_event.is_down[event.button] = True
                self._mouse_event.is_pressing[event.button] = True

            elif event.type == pygame.KEYUP:
                self._key_event.is_updated = True
                self._key_event.is_up[event.key] = True
                self._key_event.is_pressing[event.key] = False

            elif event.type == pygame.KEYDOWN:
                self._key_event.is_updated = True
                self._key_event.is_down[event.key] = True
                self._key_event.is_pressing[event.key] = True

    @property
    def is_quit(self) -> bool:
        return self._is_quit

    @property
    def is_mouse_updated(self) -> bool:
        return self._mouse_event.is_updated

    @property
    def is_mouse_up(self) -> defaultdict:
        return self._mouse_event.is_up

    @property
    def is_mouse_down(self) -> defaultdict:
        return self._mouse_event.is_down

    @property
    def is_mouse_pressing(self) -> defaultdict:
        return self._mouse_event.is_pressing

    @property
    def is_key_updated(self) -> bool:
        return self._key_event.is_updated

    @property
    def is_key_up(self) -> defaultdict:
        return self._key_event.is_up

    @property
    def is_key_down(self) -> defaultdict:
        return self._key_event.is_down

    @property
    def is_key_pressing(self) -> defaultdict:
        return self._key_event.is_pressing

    def get_mouse_pos(self) -> tuple[int, int]:
        return pygame.mouse.get_pos()
