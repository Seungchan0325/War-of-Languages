import abc
import math

import pygame
import pymunk
from pygame import Rect
from pygame.sprite import DirtySprite
from pymunk import Vec2d

from scenes.common import FPS, Text
from system.clock import Clock
from system.event_handler import EventHandler
from system.scenes import BaseScene
from system.screen import Screen

G = 980.665


"""
Map ratio = 16 : 9
1m = 100coord
1coord = screen width / 16 / 100

width: 16m
height: 9m

 ---------------
|        (16, 9)|
|               |
|(0, 0)         |
 ---------------

"""


def coord2pixel(coord: float) -> int:
    screen = Screen.instance()
    coord_per_pixel = screen.width / 16 / 100
    return round(coord * coord_per_pixel)


def coord2pixel_pos(coord: tuple[float, float]) -> tuple[int, int]:
    screen = Screen.instance()
    return (coord2pixel(coord[0]), screen.height - coord2pixel(coord[1]))


class Entity(DirtySprite):

    def __init__(self,
                 pos: tuple[float, float],
                 size: tuple[float, float]):
        super().__init__()

        self.size: tuple[float, float] = size

        width = size[0]
        height = size[1]

        vs = [(0, 0), (width, 0), (width, height), (0, height)]

        self.body: pymunk.Body = pymunk.Body()
        self.body.position = pos

        self.shape = pymunk.Poly(self.body, vs)
        self.shape.mass = 1
        self.shape.friction = 0.5
        self.shape.elasticity = 0.5

        self.rect: Rect = Rect((0, 0), (coord2pixel(self.size[0]), coord2pixel(self.size[1])))
        self.rect.bottomleft = coord2pixel_pos(self.body.position)

        surface = pygame.Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

        self.body.center_of_gravity = Vec2d(width/2, height/2)

    def apply_force(self, force: tuple[int, int]):
        self.body.apply_force_at_local_point(force, self.body.center_of_gravity)

    def apply_impulse(self, impulse: tuple[int, int]):
        self.body.apply_impulse_at_local_point(impulse, self.body.center_of_gravity)

    def update(self):
        self.dirty = 1
        self.rect.bottomleft = coord2pixel_pos(self.body.position)


class BaseInput(abc.ABC):

    @abc.abstractmethod
    def jump(self) -> bool:
        pass

    @abc.abstractmethod
    def left(self) -> bool:
        pass

    @abc.abstractmethod
    def right(self) -> bool:
        pass


class MyInput(BaseInput):

    def __init__(self):
        self.event_handler = EventHandler.instance()

    def jump(self) -> bool:
        return self.event_handler.is_key_down[pygame.K_SPACE]

    def left(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_a]

    def right(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_d]

class MyCharacter(Entity):

    def __init__(self, my_input: BaseInput):
        super().__init__((0, 0), (50, 50))
        self.input = my_input

    def update(self):
        super().update()

        if self.input.jump():
            self.apply_impulse((0, 500))

        if abs(self.body.velocity.x) < 500 and self.input.left():
            self.apply_force((-700, 0))

        if abs(self.body.velocity.x) < 500 and self.input.right():
            self.apply_force((700, 0))


class PlayScene(BaseScene):

    def __init__(self):
        super().__init__()

        self._space = pymunk.Space()
        self._space.gravity = (0, -G)

        borders = [
            pymunk.Segment(self._space.static_body, (0, 0), (1600, 0), 1),
            pymunk.Segment(self._space.static_body, (0, 900), (1600, 900), 1),
            pymunk.Segment(self._space.static_body, (0, 0), (0, 900), 1),
            pymunk.Segment(self._space.static_body, (1600, 0), (1600, 900), 1),
        ]

        for border in borders:
            border.friction = 1
            border.elasticity = 0.5

        self._space.add(*borders)

        self.register_entity(MyCharacter(MyInput()))

    def register_entity(self, entity: Entity):
        self._space.add(entity.body, entity.shape)
        entity.body.moment = math.inf
        self.sprites.add(entity)


    def update(self):
        clock = Clock.instance()
        self._space.step(clock.delta_sec())
        self.sprites.update()
