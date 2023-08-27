from dataclasses import dataclass
from time import perf_counter

import pygame
from pygame import Vector2
from pygame.sprite import DirtySprite, Group

from system.screen import Screen
from system.scenes import SceneBase
from system.event_handler import EventHandler
from system.clock import Clock
from scenes.common import FPS, Text


G = 9.80665


"""
Map ratio = 16 : 9
1m = screen width / 16

 ---------------
|        (16, 9)|
|               |
|(0, 0)         |
 ---------------

"""


def meter2pixel(meter: float) -> int:
    screen = Screen.instance()
    pixel_per_meter = screen.width / 16
    return round(meter * pixel_per_meter)


def pixel2meter(pixel: int) -> float:
    screen = Screen.instance()
    pixel_per_meter = screen.width / 16
    return pixel / pixel_per_meter


def coord2pixel(meter: tuple[float, float]) -> tuple[int, int]:
    screen = Screen.instance()
    return (meter2pixel(meter[0]), screen.height - meter2pixel(meter[1]))


def pixel2coord(pixel: tuple[float, float]) -> tuple[int, int]:
    screen = Screen.instance()
    return (pixel2meter(pixel[0]), screen.height - pixel2meter(pixel[1]))


def overlayed_line(start1: float,
                   length1: float,
                   start2: float,
                   length2: float) -> float:
    s1 = start1
    e1 = start1 + length1
    s2 = start2
    e2 = start2 + length2
    return min(e1, e2) - max(s1, s2)


@dataclass
class PhysicsData:
    position: Vector2 = Vector2(0, 0)
    velocity: Vector2 = Vector2(0, 0)
    force: Vector2
    inertia: float
    inverse_inertia: float
    mass: float
    inverse_mass: float
    static_friction: float
    dynamic_friction: float
    restitution: float
    use_gravity: bool
    is_grounded: bool


class RigidBody:

    def __init__(self, data: PhysicsData):
        self._data = data

    def reset(self):
        self._data.is_grounded = False


class RigidManager:
    def __init__(self):
        self._rigid_bodies: Group

    def update(self):
        pass


class Entity(DirtySprite):

    # Both pos and size are meters
    def __init__(self,
                 game_sprites: pygame.sprite.Group,
                 pos: tuple[float, float],
                 size: tuple[float, float]):
        super().__init__()

        self.game_sprites = game_sprites

        # Pysical Variable
        self.is_fixed: bool = False
        self.use_gravity: bool = True

        self.is_grounded: bool = False
        self.is_colliding: bool = False

        self.mass: float = 1.0

        self._acc: Vector2 = Vector2()
        self.last_acc: Vector2 = Vector2()

        self._vel: Vector2 = Vector2()
        self.last_vel: Vector2 = Vector2()

        self.static_friction: float = 0
        self.dynamic_friction: float = 0

        self.restitution: float = 1

        self.pos: Vector2 = Vector2(pos)
        self.last_pos: Vector2 = self.pos
        self.size: tuple[float, float] = size

        self.dirty = 1

        width = meter2pixel(self.size[0])
        height = meter2pixel(self.size[1])
        self.rect = pygame.Rect((0, 0), (width, height))
        self.rect.bottomleft = coord2pixel(self.pos)

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.size[0] / 2,
                              self.pos.y + self.size[1] / 2)
    
    @property
    def inverse_mass(self) -> float:
        if self.mass == 0:
            return 0
        return 1 / self.mass

    def apply_acc(self, acc: Vector2):
        self._acc += acc

    def apply_force(self, force: Vector2):
        self._acc += force / self.mass

    def apply_impulse(self, impulse: Vector2):
        pass

    def change_vel(self, vel: Vector2):
        self._vel = vel

    def rigid_update(self):
        if self.is_fixed:
            return

        clock = Clock.instance()
        delta_time = clock.delta_sec()

        self.last_acc = self._acc
        self.last_vel = self._vel

        self._vel += self._acc * delta_time

        self.last_pos = self.pos
        self.pos += self._vel * delta_time

    def collide_detection(self):
        self._acc = Vector2()

        if self.is_fixed:
            return

        if self.use_gravity:
            self.apply_acc(Vector2(0, -G))

        # collision handling
        for other in self.game_sprites:
            if other is self:
                continue

            overlayed_width = overlayed_line(self.last_pos.x, self.size[0],
                                             other.last_pos.x, other.size[0])

            overlayed_height = overlayed_line(self.last_pos.y, self.size[1],
                                              other.last_pos.y, other.size[1])

            # Did not collide
            if overlayed_width <= 0 or overlayed_height <= 0:
                continue

            # Correct position
            relative_vel = self._vel - other.last_vel

            dt = float("inf")

            angle = 0
            if relative_vel.x != 0:
                cand = overlayed_width / abs(relative_vel.x)
                if cand < dt:
                    angle = 0
                    dt = cand

            if relative_vel.y != 0:
                cand = overlayed_height / abs(relative_vel.y)
                if cand < dt:
                    angle = 90
                    dt = cand

            assert dt != float("inf")

            self.pos -= self._vel * dt

            # Compute next velocity
            normal = Vector2(1, 0)
            normal.rotate_ip(angle)

            e = (self.restitution + other.restitution) / 2
            m1 = self.mass
            v1 = self._vel.dot(normal)
            m2 = other.mass
            v2 = other.last_vel.dot(normal)

            v = ((e + 1) * m2 * v2 + v1 * (m1 - e * m2)) / (m1 + m2)

            normal_vel1 = normal * v1
            tangent_vel1 = self._vel - normal_vel1

            normal_vel1 = normal * v

            vel = normal_vel1 + tangent_vel1

            self.change_vel(vel)

    def view_update(self):
        if self.is_fixed:
            return

        self.dirty = 1
        self.rect.bottomleft = coord2pixel(self.pos)

    def update(self):
        self.is_grounded = False
        self.rigid_update()
        self.collide_detection()
        self.view_update()


class Border(Entity):

    def __init__(self,
                 game_sprites: pygame.sprite.Group,
                 pos: tuple[int, int],
                 size: tuple[int, int]):
        super().__init__(game_sprites, pos, size)
        self.mass = 1e20
        self.is_fixed = True
        self.use_gravity = False

        surface = pygame.Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

    def update(self):
        super().rigid_update()
        super().collide_detection()
        super().view_update()


class Block(Entity):

    def __init__(self,
                 game_sprites: pygame.sprite.Group,
                 pos: tuple[int, int],
                 vel: Vector2,
                 mass: float,
                 color: str):
        super().__init__(game_sprites, pos, (1, 1))

        self._vel = Vector2(vel[0], vel[1])
        self.last_vel = self._vel

        self.mass = mass
        self.restitution = 1

        self.use_gravity = True

        surface = pygame.Surface(self.rect.size)
        surface.fill(color)

        self.image = surface

    def update(self):
        super().rigid_update()
        super().collide_detection()
        super().view_update()
        # logic


class PlayScene(SceneBase):

    def __init__(self):
        super().__init__()

        self.play_sprites = pygame.sprite.Group()

        self.play_sprites.add(Block(self.play_sprites, (3, 3), (5, 0), 1, "red"))
        self.play_sprites.add(Block(self.play_sprites, (13, 0), (0, 0), 1, "white"))
        self.play_sprites.add(Border(self.play_sprites, (0, -1), (16, 1)))
        self.play_sprites.add(Border(self.play_sprites, (-1, 0), (1, 8)))
        self.play_sprites.add(Border(self.play_sprites, (16, 0), (1, 8)))

        self.sprites.add(self.play_sprites)

        self.sprites.add(FPS())

    def update(self):
        self.sprites.update()
