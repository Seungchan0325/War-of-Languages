import platform

import pygame
from pygame import Rect, Surface
from pygame.sprite import DirtySprite, Group

from game_config import GameConfig
from system.clock import Clock
from system.event_handler import EventHandler
from system.screen import Screen


def px_to_pt(px: int) -> int:
    pt = 0
    if platform.system() == "Windows":
        # Convert px to pt
        pt = round(px * 72 / 96)
    else:
        pt = px
    return pt


def render_text(text: str, px: int) -> Surface:
    pt = px_to_pt(px)
    font_name = GameConfig.instance().font
    font = pygame.font.SysFont(font_name, pt)
    return font.render(text, True, "white")


class RatioCoord:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        assert False, "Invalied index"

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


class RatioRect:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x: float = x
        self.y: float = y
        self.w: float = w
        self.h: float = h

    def to_pyrect(self) -> Rect:
        screen = Screen.instance()
        x = screen.width * self.x
        y = screen.height * self.y
        w = screen.width  * self.w
        h = screen.height * self.h
        return Rect(x, y, w, h)

    @property
    def left(self) -> float:
        return self.x

    @left.setter
    def left(self, value: float):
        self.x = value

    @property
    def right(self) -> float:
        return self.x + self.w

    @right.setter
    def right(self, value: float):
        self.x = value - self.w

    @property
    def top(self) -> float:
        return self.y

    @top.setter
    def top(self, value: float):
        self.y = value

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @bottom.setter
    def bottom(self, value: float):
        self.y = value - self.h

    @property
    def centerx(self) -> float:
        return self.x + self.w / 2

    @centerx.setter
    def centerx(self, value: float):
        self.x = value - self.w / 2

    @property
    def centery(self) -> float:
        return self.y + self.h / 2

    @centery.setter
    def centery(self, value: float):
        self.y = value - self.h / 2

    @property
    def center(self) -> RatioCoord:
        return (self.centerx, self.centery)

    @center.setter
    def center(self, value: RatioCoord):
        self.centerx = value[0]
        self.centery = value[1]


class Text(DirtySprite):

    def __init__(self,
                 text: str,
                 rect: RatioRect,
                 fit_width: bool = True):
        super().__init__()

        self.text = text
        self.fit_width = fit_width

        self.rect = rect.to_pyrect()

        self.dirty = 1
        self.image = self._create_surface()

    def _create_surface(self) -> pygame.Surface:
        rendered_text = render_text(self.text, self.rect.height)

        if self.fit_width:
            self.rect.width = rendered_text.get_rect().width

        surface = pygame.Surface(self.rect.size)

        normal_rect = self.rect.copy()
        normal_rect.topleft = (0, 0)
        dest = rendered_text.get_rect(
            center=normal_rect.center
        )

        surface.blit(rendered_text, dest)

        return surface

    def set_text(self, text: str):
        self.dirty = 1
        self.text = text
        self.image = self._create_surface()


class Title(Text):

    def __init__(self):
        name = GameConfig.instance().name

        rect = RatioRect(0, 0.16, 0.85, 0.15)
        rect.centerx = 0.5

        super().__init__(name, rect, False)


class FPS(Text):

    def __init__(self, rect: RatioRect):
        text = self._get_text()
        super().__init__(text, rect, False)

    def _get_text(self) -> str:
        clock = Clock.instance()
        fps = clock.fps()
        text = f"{fps: .2f}"
        return text

    def update(self):
        text = self._get_text()
        self.set_text(text)


class Button(DirtySprite):

    def __init__(self, rect: RatioRect):
        super().__init__()

        self._event_handler = EventHandler.instance()

        self.rect = rect.to_pyrect()
        self._prev_on_mouse = self.is_on_mouse()

    def update_position(self, ratio_rect: RatioRect):
        if self.rect == ratio_rect.to_pyrect():
            return
        self.dirty = 1
        self.rect = ratio_rect.to_pyrect()

    def is_on_mouse(self) -> bool:
        mouse_pos = self._event_handler.get_mouse_pos()
        return self.rect.collidepoint(mouse_pos)

    def mouse_enter(self) -> bool:
        return not self._prev_on_mouse and self.is_on_mouse()

    def mouse_exit(self) -> bool:
        return self._prev_on_mouse and not self.is_on_mouse()

    def is_clicked(self, button: int) -> bool:
        mouse_down = self._event_handler.is_mouse_down[button]
        return mouse_down and self.is_on_mouse()

    def is_up_clicked(self, button: int) -> bool:
        mouse_down = self._event_handler.is_mouse_up[button]
        return mouse_down and self.is_on_mouse()

    def update(self):
        self._prev_on_mouse = self.is_on_mouse()


class ButtonList(DirtySprite):

    def __init__(self,
                 area: RatioRect,
                 button_size: RatioRect):
        super().__init__()

        self.sprites: Group = Group()
        self.buttons: list[Button] = []

        self.area: RatioRect = area
        self.rect: Rect = self.area.to_pyrect()

        self._bg = Surface(Screen.instance().size)
        self._bg.fill("gray")

        surface = self._bg.subsurface(self.rect)
        self.image = surface

        self._scroll_cnt = 0
        self._button_size = button_size

        self._draw = False

    def _compute_position(self, index: int) -> RatioRect:
        x = self.area.x
        y = (index + self._scroll_cnt) * self._button_size.h + self.area.y
        w = self._button_size.w
        h = self._button_size.h
        return RatioRect(x, y, w, h)

    def add_button(self, button: Button):
        idx = len(self.buttons)
        pos = self._compute_position(idx)
        button.update_position(pos)

        self.sprites.add(button)
        self.buttons.append(button)

        self._draw = True

    def update_position(self):
        for i, button in enumerate(self.buttons):
            pos = self._compute_position(i)
            button.update_position(pos)

    def update(self):
        event_handler = EventHandler.instance()

        # Scroll
        if self.rect.collidepoint(event_handler.get_mouse_pos()):
            max_cnt = 0
            min_cnt = 1 - len(self.buttons)
            if event_handler.mouse_scroll < 0 and min_cnt < self._scroll_cnt:
                self._scroll_cnt -= 1
                self._draw = True
            elif event_handler.mouse_scroll > 0 and self._scroll_cnt < max_cnt:
                self._draw = True
                self._scroll_cnt += 1

        if self._draw:
            self.update_position()

        self.sprites.update()

        # Check if It need to draw
        for sprite in self.sprites:
            if sprite.dirty > 0:
                self._draw = True
                break

        if self._draw:
            self.dirty = 1

            surface = self._bg.copy()
            self.sprites.draw(surface)
            surface = surface.subsurface(self.rect)

            self.image = surface

        self._draw = False
