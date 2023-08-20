import pygame

from system import scene_base
from window import Window
from game_config import GameConfig

class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        text_color = (255, 255, 255)
        self._title_font = pygame.font.SysFont("arial", 30)
        self._text = self._title_font.render(GameConfig.instance().name, True, text_color)
        self._window = Window.instance()

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        screen.fill("black")

        screen.blit(self._text, self._window.get_center())
