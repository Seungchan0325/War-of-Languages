import abc

import pygame

from system.systems import EventManager


class Button(abc.ABC):

    def __init__(self, rect: pygame.Rect):
        self._rect = rect
        self._event_manager = EventManager.instance()

    def is_on_mouse(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    def is_clicked(self) -> bool:
        mouse_down = self._event_manager.is_mouse_down(pygame.BUTTON_LEFT)
        return self.is_on_mouse() and mouse_down

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def render(self, screen: pygame.Surface):
        pass
