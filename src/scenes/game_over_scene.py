import pygame
from pygame import Surface
from pygame.sprite import DirtySprite

from scenes.common import RatioRect, RatioCoord, Button, render_text
from system.scenes import BaseScene, Scenes
from system.screen import Screen


class GameOverMenu(DirtySprite):

    def __init__(self, winner: str):
        super().__init__()
        self.winner = winner

        rect = RatioRect(0, 0, 0.3, 0.8)
        rect.center = RatioCoord(0.5, 0.5)
        self.rect = rect.to_pyrect()

        self.image = self._create_surface()

    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)
        surface.fill("purple")

        px = int(self.rect.height * 0.1)
        text = render_text(f"Winner: {self.winner}", px)

        dest = text.get_rect(
            center=surface.get_rect().center
        )

        surface.blit(text, dest)

        return surface


class BackButton(Button):

    def __init__(self):
        rect = RatioRect(0, 0, 0.1, 0.1)
        super().__init__(rect)

        self.image = self._create_surface()

    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("red")
        else:
            surface.fill("purple")

        text = render_text("back", int(self.rect.height * 0.8))

        dest = text.get_rect(
            center=surface.get_rect().center
        )

        surface.blit(text, dest)

        return surface

    def update(self):
        if self.mouse_enter() or self.mouse_exit():
            self.dirty = 1
            self.image = self._create_surface()

        if self.is_up_clicked(pygame.BUTTON_LEFT):
            from scenes.title_scene import TitleScene
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())


class GameOverScene(BaseScene):

    def __init__(self, winner: str):
        super().__init__()

        self.sprites.add(GameOverMenu(winner))
        self.sprites.add(BackButton())

    def render(self):
        screen = Screen.instance()
        screen.render(self.background, self.sprites)
