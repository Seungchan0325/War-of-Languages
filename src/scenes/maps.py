import abc
from enum import Enum, auto

import pygame
from pygame import Rect, Surface
from pygame.sprite import DirtySprite, Group
import pymunk
from pymunk import Body, Poly, Segment, Space

from system.clock import Clock
from system.event_handler import EventHandler
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


class Lenght:

    def __init__(self, x: float):
        self.x: float = x

    def to_px(self) -> int:
        screen = Screen.instance()
        pixel_per_coord = screen.width / 16 / 100
        return round(self.x * pixel_per_coord)


class Size:

    def __init__(self, width: float, height: float):
        self.width = Lenght(width)
        self.height = Lenght(height)

    def to_tuple(self) -> tuple[float, float]:
        return (self.width.x, self.height.x)

    def to_px(self) -> tuple[int, int]:
        return (self.width.to_px(), self.height.to_px())


class Coord:

    def __init__(self, x: float, y: float):
        self.x = Lenght(x)
        self.y = Lenght(y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x.x, self.y.x)

    def to_px(self) -> tuple[int, int]:
        screen = Screen.instance()
        return (self.x.to_px(), screen.height - self.y.to_px())


class CollisionTypes(Enum):
    GROUND = auto()
    PLAYER = auto()


class Entity(DirtySprite):

    def __init__(self, space: Space, pos: Coord, size: Size):
        super().__init__()

        self.pos: Coord = pos
        self.size: Size = size

        self.body: Body = Body(2, float("inf"))
        self.body.position = self.pos.to_tuple()

        width = self.size.width.x
        height = self.size.height.x

        vs = [
            (0, 0),
            (width, 0),
            (width, height),
            (0, height),
        ]

        self.shape = Poly(self.body, vs)
        self.shape.friction = 0.8
        self.shape.elasticity = 0.5

        space.add(self.body, self.shape)

        self.rect = Rect(self.pos.to_px(), self.size.to_px())

        surface = Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

    def apply_force(self, force: tuple[int, int]):
        self.body.apply_force_at_local_point(force, self.body.center_of_gravity)

    def apply_impulse(self, impulse: tuple[int, int]):
        self.body.apply_impulse_at_local_point(impulse, self.body.center_of_gravity)

    def collision_begin(self, arbiter: pymunk.Arbiter, space: pymunk.Space):
        pass

    def collision_end(self, arbiter: pymunk.Arbiter, space: pymunk.Space):
        pass

    def update(self):
        self.dirty = 1
        self.pos = Coord(self.body.position[0], self.body.position[1])
        self.rect.bottomleft = self.pos.to_px()


class BaseMap:

    def __init__(self):
        self.space = Space()
        self.space.gravity = (0, -G)

        width = 1600
        height = 900

        borders = [
            Segment(self.space.static_body, (0, 0), (width, 0), 1),
            Segment(self.space.static_body, (0, height), (width, height), 1),
            Segment(self.space.static_body, (0, 0), (0, height), 1),
            Segment(self.space.static_body, (width, 0), (width, height), 1),
        ]

        borders[0].friction = 0.8
        borders[0].elasticity = 0.5
        borders[0].collision_type = CollisionTypes.GROUND.value
        for border in borders[1:]:
            border.friction = 0
            border.elasticity = 1

        self.space.add(*borders)

        self.sprites: Group = Group()

        def default_begin_handler(arbiter: pymunk.Arbiter, space: Space, data) -> bool:
            for i in self.sprites:
                if i.shape in arbiter.shapes:
                    i.collision_begin(arbiter, space)
            return True

        def default_end_handler(arbiter: pymunk.Arbiter, space: Space, data):
            for i in self.sprites:
                if i.shape in arbiter.shapes:
                    i.collision_end(arbiter, space)

        handler = self.space.add_default_collision_handler()
        handler.begin = default_begin_handler
        handler.separate = default_end_handler

    def update(self):
        clock = Clock.instance()
        self.space.step(clock.delta_sec())
        self.sprites.update()


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


class Character(Entity):

    def __init__(self, space: Space, pos: Coord, my_input: BaseInput):
        super().__init__(space, pos, Size(50, 50))
        self.shape.collision_type = CollisionTypes.PLAYER.value
        self.input = my_input
        self.speed = 3000
        self.jump = 1400
        self.limit_speed = 300
        self.grounded_cnt = 0

    def collision_begin(self, arbiter: pymunk.Arbiter, space: Space):
        other = None
        if arbiter.shapes[0] is self.shape:
            other = arbiter.shapes[1]
        elif arbiter.shapes[1] is self.shape:
            other = arbiter.shapes[0]
        else:
            assert False, "Invalied arbiter"

        if other.collision_type == CollisionTypes.GROUND.value:
            self.grounded_cnt += 1
        return True

    def collision_end(self, arbiter: pymunk.Arbiter, space: Space):
        other = None
        if arbiter.shapes[0] is self.shape:
            other = arbiter.shapes[1]
        elif arbiter.shapes[1] is self.shape:
            other = arbiter.shapes[0]
        else:
            assert False, "Invalied arbiter"

        if other.collision_type == CollisionTypes.GROUND.value:
            self.grounded_cnt -= 1

    def update(self):
        super().update()

        if self.grounded_cnt > 0 and self.input.jump():
            self.apply_impulse((0, self.jump))

        if -self.limit_speed < self.body.velocity.x and self.input.left():
            self.apply_force((-self.speed, 0))

        if self.body.velocity.x < self.limit_speed and self.input.right():
            self.apply_force((self.speed, 0))

class MyInput(BaseInput):

    def __init__(self):
        self.event_handler = EventHandler.instance()

    def jump(self) -> bool:
        return self.event_handler.is_key_down[pygame.K_SPACE]

    def left(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_a]

    def right(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_d]


class EmemyInput(BaseInput):

    def __init__(self):
        self.event_handler = EventHandler.instance()

    def jump(self) -> bool:
        return self.event_handler.is_key_down[pygame.K_UP]

    def left(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_LEFT]

    def right(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_RIGHT]


class Taskbar(Entity):

    def __init__(self, space: Space):
        super().__init__(space, Coord(0, 0), Size(1600, 50))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.STATIC


class Icon(Entity):

    def __init__(self, space: Space, pos: Coord):
        super().__init__(space, pos, Size(40, 40))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.STATIC


class WindowsMap(BaseMap):

    def __init__(self):
        super().__init__()

        for i in range(3):
            for j in range(10):
                self.sprites.add(Icon(self.space, Coord(j * 100 + 330, i * 230 + 100)))

        self.sprites.add(Taskbar(self.space))
        self.sprites.add(Character(self.space, Coord(0, 100), MyInput()))
        self.sprites.add(Character(self.space, Coord(1550, 100), EmemyInput()))
