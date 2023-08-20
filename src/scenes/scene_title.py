import pygame

from system import scene_base

class SceneTitle(scene_base.SceneBase):

    def __init__(self):
        pass

    def update(self):
        pass

    def render(self, screen: pygame.Surface):
        screen.fill("white")
