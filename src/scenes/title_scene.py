import pygame
from pygame import Surface

from scenes.common import Button, RatioRect, Title, render_text
from scenes.selection_scene import SelectionScene
from system.scenes import BaseScene, Scenes
from system.screen import Screen


class TemplateButton(Button):

    def __init__(self, rect: RatioRect, text: str):
        super().__init__(rect)

        self.dirty = 1

        self.text = text

        self.image = self._create_surface()

    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("red")
        else:
            surface.fill("purple")

        rendered_text = render_text(self.text, int(self.rect.height * 0.5))

        normal_rect = self.rect.copy()
        normal_rect.topleft = (0, 0)
        dest = rendered_text.get_rect(
            center=normal_rect.center
        )
        surface.blit(rendered_text, dest)

        return surface


    def update(self):
        if self.mouse_enter() or self.mouse_exit():
            self.dirty = 1
            self.image = self._create_surface()

        super().update()


class PlayButton(TemplateButton):

    def __init__(self):
        rect = RatioRect(0, 0.48, 0.28, 0.1)
        rect.centerx = 0.5

        super().__init__(rect, "{ Play }")

    def update(self):
        if self.is_up_clicked(pygame.BUTTON_LEFT):
            scenes = Scenes.instance()
            scenes.change_scene(SelectionScene())

        super().update()


class SettingsButton(TemplateButton):

    def __init__(self):

        rect = RatioRect(0, 0.63, 0.28, 0.1)
        rect.centerx = 0.5

        super().__init__(rect, "{ Settings }")


class TitleScene(BaseScene):

    def __init__(self):
        super().__init__()

        self.sprites.add(Title())
        self.sprites.add(PlayButton())
        self.sprites.add(SettingsButton())

    def update(self):
        super().update()

        self.sprites.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self.background, self.sprites)
