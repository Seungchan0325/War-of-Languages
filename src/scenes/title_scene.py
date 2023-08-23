import pygame

from system.control.button import Button
from system.scenes import SceneBase
from system.screen import Screen
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

    def update(self):
        if self.is_clicked(pygame.BUTTON_LEFT):
            self.dirty = 1
            self._state ^= 1
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


class TitleScene(SceneBase):

    def __init__(self):
        super().__init__()

        self.sprites.add(Title())
        self.sprites.add(PlayButton())
        self.sprites.add(SettingsButton())

    def update(self):
        self.sprites.update()
