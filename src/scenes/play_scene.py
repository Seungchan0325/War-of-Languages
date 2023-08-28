from time import perf_counter

import pygame
from pygame import Vector2, Rect
from pygame.sprite import Group, DirtySprite

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


class RigidBody:

    def __init__(self):
        self.position: Vector2 = Vector2()
        self.size: tuple[int, int] = (1, 1)

        self.mass: float = 1

        self.velocity: Vector2 = Vector2()
        self.last_velocity: Vector2 = Vector2()
        self.force: Vector2 = Vector2()
        self.acceleration: Vector2 = Vector2()
        self.impulse: Vector2 = Vector2()

        self.static_friction: float = 0
        self.dynamic_friction: float = 0

        self.restitution: float = 1

        self.use_gravity: bool = True
        self.is_grounded: bool = False
        self.is_colliding: bool = False
        self.is_fixed: bool = False

    @property
    def inverse_mass(self) -> float:
        if self.mass == 0:
            return 0
        return 1 / self.mass

    def apply_force(self, force: Vector2):
        self.force += force

    def apply_acceleration(self, acceleration: Vector2):
        self.acceleration += acceleration

    def apply_impulse(self, impulse: Vector2):
        self.impulse += impulse

    def add_velocity(self, velocity: Vector2):
        self.velocity += velocity

    def change_velocity(self, velocity: Vector2):
        self.velocity = velocity

    def reset_forces(self):
        self.is_grounded = False
        self.is_colliding = False
        self.force = Vector2()
        self.acceleration = Vector2()
        self.impulse = Vector2()

    def rigid_update(self):
        if self.is_fixed:
            return
        delta_time = Clock.instance().delta_sec()

        if self.use_gravity:
            self.apply_acceleration(Vector2(0, -G))

        self.velocity += self.acceleration * delta_time
        self.velocity += self.acceleration * self.inverse_mass * delta_time
        self.velocity += self.impulse * self.inverse_mass

        self.last_velocity = self.velocity
        self.position += self.velocity * delta_time


class RigidManager:

    def __init__(self):
        self.bodies: list[RigidBody] = []

    def add(self, body: RigidBody):
        self.bodies.append(body)

    def compute_penetration(self,
                            body_a: RigidBody,
                            body_b: RigidBody) -> tuple[float, float]:
        penetration_width = overlayed_line(body_a.position.x, body_a.size[0],
                                         body_b.position.x, body_b.size[0])

        penetration_height = overlayed_line(body_a.position.y, body_a.size[1],
                                          body_b.position.y, body_b.size[1])

        return (penetration_width, penetration_height)

    # Correct position and Return normal vector
    def correct_position(self,
                         body_a: RigidBody,
                         body_b: RigidBody,
                         penetration: tuple[float, float]) -> Vector2:
        relative_velocity = body_a.last_velocity - body_b.last_velocity

        dt = float("inf")
        angle = 0
        if relative_velocity.x != 0:
            cand = penetration[0] / abs(relative_velocity.x)
            if dt > cand:
                dt = cand
                angle = 0

        if relative_velocity.y != 0:
            cand = penetration[1] / abs(relative_velocity.y)
            if dt > cand:
                dt = cand
                angle = 90

        assert dt != float("inf")

        body_a.position -= body_a.velocity * dt
        body_b.position -= body_b.velocity * dt

        ret = Vector2(1, 0)
        ret.rotate_ip(angle)

        return ret

    def collision_handling(self,
                           body_a: RigidBody,
                           body_b: RigidBody,
                           normal: Vector2):
        e = (body_a.restitution + body_b.restitution) / 2

        u1 = body_a.velocity.dot(normal)
        u2 = body_b.velocity.dot(normal)

        normal_vel1 = normal * u1
        normal_vel2 = normal * u2

        tangent_vel1 = body_a.velocity - normal_vel1
        tangent_vel2 = body_b.velocity - normal_vel2

        m1 = body_a.mass
        m2 = body_b.mass

        v1 = ((e + 1) * m2 * u2 + u1 * (m1 - e * m2)) / (m1 + m2)
        v2 = ((e + 1) * m1 * u1 + u2 * (m2 - e * m1)) / (m1 + m2)

        normal_vel1 = normal * v1
        normal_vel2 = normal * v2

        body_a.velocity = normal_vel1 + tangent_vel1
        body_b.velocity = normal_vel2 + tangent_vel2

    def update(self):
        for body in self.bodies:
            body.rigid_update()
            body.reset_forces()

        for i, body_a in enumerate(self.bodies):
            for body_b in self.bodies[i+1:]:
                penetration = self.compute_penetration(body_a, body_b)

                # Did not collided
                if penetration[0] <= 0 or penetration[1] <= 0:
                    continue

                body_a.is_colliding = True
                body_b.is_colliding = True

                normal = self.correct_position(body_a, body_b, penetration)

                self.collision_handling(body_a, body_b, normal)


class NewEntity(DirtySprite):

    def __init__(self):
        super().__init__()
        self.rigid_body: RigidBody = RigidBody()

        width = meter2pixel(self.rigid_body.size[0])
        height = meter2pixel(self.rigid_body.size[1])
        self.rect: Rect = Rect(coord2pixel(self.rigid_body.position), (width, height))

        surface = pygame.Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

    def update(self):
        self.dirty = 1
        self.rect.bottomleft = coord2pixel(self.rigid_body.position)


class PlayScene(SceneBase):

    def __init__(self):
        super().__init__()

        # self.play_sprites = pygame.sprite.Group()

        # self.play_sprites.add(Block(self.play_sprites, (3, 1), (5, 0), 1, "red"))
        # self.play_sprites.add(Block(self.play_sprites, (13, 0), (0, 0), 1, "white"))
        # self.play_sprites.add(Border(self.play_sprites, (0, -1), (16, 1)))
        # self.play_sprites.add(Border(self.play_sprites, (-1, 0), (1, 8)))
        # self.play_sprites.add(Border(self.play_sprites, (16, 0), (1, 8)))

        # self.sprites.add(self.play_sprites)

        # self.sprites.add(FPS())

        self.rigid_manager = RigidManager()

        self.entity1 = NewEntity()
        self.entity1.rigid_body.velocity = Vector2(2, 0)
        self.entity1.rigid_body.use_gravity = False
        self.rigid_manager.add(self.entity1.rigid_body)
        self.sprites.add(self.entity1)

        self.entity2 = NewEntity()
        self.entity2.rigid_body.position = Vector2(15, 0)
        self.entity2.rigid_body.velocity = Vector2(-2, 0)
        self.rigid_manager.add(self.entity2.rigid_body)
        self.sprites.add(self.entity2)

        border = NewEntity()
        border.rigid_body.position = Vector2(0, -1)
        border.rigid_body.size = (16, 1)
        border.rigid_body.is_fixed = True
        border.rigid_body.use_gravity = False
        border.rigid_body.mass = 1e20
        self.rigid_manager.add(border.rigid_body)
        self.sprites.add(border)

    def update(self):
        self.rigid_manager.update()
        self.sprites.update()

        print("Entity 1: ", self.entity1.rigid_body.velocity,
              "Entity 2: ", self.entity2.rigid_body.velocity)

        event_handler = EventHandler.instance()

        if event_handler.is_key_pressing[pygame.K_a]:
            self.entity2.rigid_body.apply_acceleration(Vector2(-1, 0))
        if event_handler.is_key_pressing[pygame.K_d]:
            self.entity2.rigid_body.apply_acceleration(Vector2(1, 0))
