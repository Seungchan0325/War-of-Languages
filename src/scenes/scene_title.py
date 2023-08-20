import pygame

from system import scene_base

class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        text_color = (255, 255, 255)
        self._title_font = pygame.font.SysFont("arial", 30)
        self._text = self._title_font.render("War of Languages", True, text_color)

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        screen.fill("black")

        screen.blit(self._text, (100, 100))
