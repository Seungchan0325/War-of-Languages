import pygame

from game_config import GameConfig
from system.screen import Screen
from system.clock import Clock


class Title(pygame.sprite.DirtySprite):

    def __init__(self):
        super().__init__()

        screen = Screen.instance()

        width = screen.width * 0.85
        height = screen.height * 0.23
        self.rect = pygame.Rect((0, 0), (width, height))
        self.rect.centerx = screen.area.centerx
        self.rect.top = screen.height * 0.16

        config = GameConfig.instance()

        text_color = (255, 255, 255)
        text_font = pygame.font.SysFont("arial", int(self.rect.height * 0.8))
        rendered_text = text_font.render(config.name, True, text_color)

        surface = pygame.Surface(self.rect.size)
        surface.fill("purple")

        dest = rendered_text.get_rect(center=surface.get_rect().center)
        surface.blit(rendered_text, dest)

        self.image = surface

    def update(self):
        pass


class FPS(pygame.sprite.DirtySprite):

    def __init__(self):
        super().__init__()

        self.dirty = 2

        surface = self._make_surface()
        self.rect = pygame.Rect((0, 0), surface.get_size())

        self.image = self._make_surface()

    def _make_surface(self) -> pygame.Surface:
        text_color = (255, 255, 255)
        font = pygame.font.SysFont("arial", 18)

        clock = Clock.instance()
        rendered_text = font.render(f"{1000 // clock.delta()}", True, text_color)

        surface = pygame.Surface(rendered_text.get_size())

        surface.blit(rendered_text, (0, 0))

        return surface

    def update(self):
        surface = self._make_surface()
        self.rect = pygame.Rect((0, 0), surface.get_size())
        self.image = self._make_surface()
