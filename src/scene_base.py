import abc

import pygame


class SceneBase(abc.ABC):

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def render(self, screen: pygame.Surface):
        pass
