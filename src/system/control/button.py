from abc import ABC

import pygame
from pygame import Rect
from pygame.sprite import DirtySprite, Group

from system.event_handler import EventHandler
from system.screen import RatioRect, Screen


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


class ButtonList(DirtySprite):

    def __init__(self,
                 area: RatioRect,
                 button_size: RatioRect):
        super().__init__()

        self.area: RatioRect = area

        self.rect: Rect = self.area.to_pyrect()

        surface = pygame.Surface(self.rect.size)
        self.image = surface

        self._scroll_cnt = 0
        self._button_size = button_size

        self._draw = False

        self.sprites: Group = Group()
        self.buttons: list[Button] = []

    def _compute_position(self, index: int) -> RatioRect:
        x = self.area.x
        y = (index + self._scroll_cnt) * self._button_size.h + self.area.y
        w = self._button_size.w
        h = self._button_size.h
        return RatioRect(x, y, w, h)

    def add_button(self, button: Button):
        pos = self._compute_position(len(self.buttons))
        button.update_position(pos)

        self.sprites.add(button)
        self.buttons.append(button)
        self._draw = True
        self._is_scrolled = False

    def update(self):
        event_handler = EventHandler.instance()
        if self.rect.collidepoint(event_handler.get_mouse_pos()):
            if event_handler.mouse_scroll < 0 and self._scroll_cnt < 0:
                self._scroll_cnt += 1
                self._is_scrolled = True
            elif event_handler.mouse_scroll > 0 and self._scroll_cnt > -len(self.buttons) + 1:
                self._scroll_cnt -= 1
                self._is_scrolled = True

        if self._is_scrolled:
            for i, button in enumerate(self.buttons):
                pos = self._compute_position(i)
                button.update_position(pos)

        self.sprites.update()

        for sprite in self.sprites:
            if sprite.dirty > 0:
                self._draw = True
                break

        if self._draw:
            self.dirty = 1
            surface = pygame.Surface(Screen.instance().size)
            surface.fill("red")
            self.sprites.draw(surface)
            self.image = surface.subsurface(self.area.to_pyrect())

        self._draw = False
        self._is_scrolled = False
