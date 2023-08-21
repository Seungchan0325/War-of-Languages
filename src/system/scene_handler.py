import pygame

from system import scene_base
from common import SingletonInstane


class SceneHandler(SingletonInstane):

    def __init__(self):
        self._scene = None

    def change_scene(self, scene: scene_base.SceneBase):
        self._scene = scene

    def update(self):
        self._scene.update()

    def render(self, screen: pygame.Surface):
        self._scene.render(screen)
