import pygame

import scene_base


class SceneManager:

    def __init__(self, scene: scene_base.SceneBase):
        self._scene = scene

    def change_scene(self, scene: scene_base.SceneBase):
        self._scene = scene

    def update(self):
        self._scene.update()

    def render(self, screen: pygame.Surface):
        self._scene.render(screen)
