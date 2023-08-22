import abc

import pygame

from system.event_handler import EventHandler


class Button(abc.ABC, pygame.sprite.DirtySprite):

    def __init__(self, rect: pygame.Rect):
        super().__init__()

        self.rect = rect

    def is_on_mouse(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, button: int) -> bool:
        event_handler = EventHandler.instance()
        mouse_down = event_handler.is_mouse_down[button]
        return mouse_down and self.is_on_mouse()
