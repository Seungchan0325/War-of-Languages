import pygame

from system.control.button import Button
from system.scenes import BaseScene, Scenes
from system.screen import Screen, create_rect
from system.clock import Timer
from scenes.common import Title
from scenes.selection_scene import SelectionScene


class TemplateButton(Button):

    def __init__(self, rect: pygame.Rect, text: str):
        super().__init__(rect)

        self.dirty = 1

        text_color = (255, 255, 255)
        text_font = pygame.font.SysFont("arial", int(self.rect.height * 0.43))
        self.rendered_text = text_font.render(text, True, text_color)

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

        rect = create_rect(0, 0.48, 0.28, 0.1)
        rect.centerx = screen.area.centerx

        super().__init__(rect, "{ Play }")

    def update(self):
        if self._timer.over():
            scenes = Scenes.instance()
            scenes.change_scene(SelectionScene())

        super().update()


class SettingsButton(TemplateButton):

    def __init__(self):
        screen = Screen.instance()

        rect = create_rect(0, 0.63, 0.28, 0.1)
        rect.centerx = screen.area.centerx

        super().__init__(rect, "{ Settings }")


class TitleScene(BaseScene):

    def __init__(self):
        super().__init__()

        self.sprites.add(Title())
        self.sprites.add(PlayButton())
        self.sprites.add(SettingsButton())

    def update(self):
        self.sprites.update()
