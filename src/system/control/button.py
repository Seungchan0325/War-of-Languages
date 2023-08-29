from abc import ABC

from pygame import Rect
from pygame.sprite import DirtySprite

from system.event_handler import EventHandler
from system.screen import RatioRect


class Button(ABC, DirtySprite):

    def __init__(self, rect: Rect):
        super().__init__()

        self.rect = rect

    def update_position(self, ratio_rect: RatioRect):
        self.dirty = 1
        self.rect = ratio_rect.to_pyrect()

    def is_on_mouse(self) -> bool:
        event_handler = EventHandler.instance()
        mouse_pos = event_handler.get_mouse_pos()
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, button: int) -> bool:
        event_handler = EventHandler.instance()
        mouse_down = event_handler.is_mouse_down[button]
        return mouse_down and self.is_on_mouse()

    def is_up_clicked(self, button: int) -> bool:
        event_handler = EventHandler.instance()
        mouse_down = event_handler.is_mouse_up[button]
        return mouse_down and self.is_on_mouse()
