import pygame

from system.control.button import Button
from system.scenes import SceneBase
from system.screen import Screen
from system.clock import Clock, Timer
from scenes.common import (
    Title,
)


class TemplateButton(Button):

    def __init__(self, rect: pygame.Rect, text: str):
        super().__init__(rect)

        self.dirty = 1

        text_color = (255, 255, 255)
        text_font = pygame.font.SysFont("arial", int(self.rect.height * 0.43))
        self.rendered_text = text_font.render(text, True, text_color)

        #self._state = self.is_on_mouse()
        self._state = False

        surface1 = pygame.Surface(self.rect.size)
        surface1.fill("purple")

        dest = self.rendered_text.get_rect(center=surface1.get_rect().center)
        surface1.blit(self.rendered_text, dest)

        surface2 = pygame.Surface(self.rect.size)
        surface2.fill("red")

        dest = self.rendered_text.get_rect(center=surface2.get_rect().center)
        surface2.blit(self.rendered_text, dest)

        self._surfaces = [surface1, surface2]

        self.image = self._surfaces[self._state]

        self._timer = Timer(500)

    def update(self):
        if self.is_clicked(pygame.BUTTON_LEFT):
            self.dirty = 1
            self._state = 1
            self.image = self._surfaces[self._state]
            self._timer.start()

        if self._timer.over():
            self._timer.stop()
            self.dirty = 1
            self._state = 0
            self.image = self._surfaces[self._state]


class PlayButton(TemplateButton):

    def __init__(self):
        screen = Screen.instance()

        width = screen.width * 0.28
        height = screen.height * 0.1

        rect = pygame.Rect((0, 0), (width, height))

        rect.centerx = screen.area.centerx
        rect.top = screen.height * 0.48

        super().__init__(rect, "{ Play }")


class SettingsButton(TemplateButton):

    def __init__(self):
        screen = Screen.instance()

        width = screen.width * 0.28
        height = screen.height * 0.1

        rect = pygame.Rect((0, 0), (width, height))

        rect.centerx = screen.area.centerx
        rect.top = screen.height * 0.63

        super().__init__(rect, "{ Settings }")


class FPS(pygame.sprite.DirtySprite):

    def __init__(self):
        super().__init__()

        self.dirty = 2

        self.rect = pygame.Rect((0, 0), (100, 100))

        self.image = self._make_surface()

    def _make_surface(self) -> pygame.Surface:
        text_color = (255, 255, 255)
        font = pygame.font.SysFont("arial", 18)

        surface = pygame.Surface(self.rect.size)

        clock = Clock.instance()
        rendered_text = font.render(str(clock.delta()), True, text_color)
        surface.blit(rendered_text, (0, 0))

        return surface

    def update(self):
        self.image = self._make_surface()


class TitleScene(SceneBase):

    def __init__(self):
        super().__init__()

        self.sprites.add(Title())
        self.sprites.add(PlayButton())
        self.sprites.add(SettingsButton())
        self.sprites.add(FPS())

    def update(self):
        self.sprites.update()
