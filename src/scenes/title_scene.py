import pygame
from pygame import Surface

from scenes.common import Button, RatioRect, render_text
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
            surface.fill("#3d3d3d")
        else:
            surface.fill("#9caeb5")

        rendered_text = render_text(self.text, int(self.rect.height * 0.7))

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
        rect = RatioRect(0, 0.6, 0.15, 0.07)
        rect.centerx = 0.5

        super().__init__(rect, "Play")

    def update(self):
        if self.is_up_clicked(pygame.BUTTON_LEFT):
            from scenes.play_scene import PlayScene
            scenes = Scenes.instance()
            scenes.change_scene(PlayScene())

        super().update()


class TitleScene(BaseScene):

    def __init__(self):
        super().__init__()

        background = pygame.image.load("resources/start.png")
        background = pygame.transform.scale(background, Screen.instance().size)
        self.background = background

        self.sprites.add(PlayButton())

    def update(self):
        super().update()

        self.sprites.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self.background, self.sprites)
