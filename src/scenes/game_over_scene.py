import pygame
from pygame import Surface
from pygame.sprite import DirtySprite

from scenes.common import RatioRect, RatioCoord, Button, render_text
from system.scenes import BaseScene, Scenes
from system.screen import Screen


class BackButton(Button):

    def __init__(self):
        rect = RatioRect(0, 0, 0.07, 0.05)
        super().__init__(rect)

        self.image = self._create_surface()

    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("#3d3d3d")
        else:
            surface.fill("#9caeb5")

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
        super().update()


class GameOverScene(BaseScene):

    def __init__(self, winner: str):
        super().__init__()

        background: Surface
        if winner == "Player 1":
            background = pygame.image.load("resources/p1win.png")
        elif winner == "Player 2":
            background = pygame.image.load("resources/p2win.png")
        background = pygame.transform.scale(background, Screen.instance().size)
        self.background = background

        self.sprites.add(BackButton())

    def update(self):
        self.sprites.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self.background, self.sprites)
