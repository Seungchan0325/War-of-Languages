import time

import pygame

from common import SingletonInstane
from game_config import GameConfig


SECOND_MS = 1000
SECOND_NS = 1000000


class Clock(SingletonInstane):

    def __init__(self):
        self._clock: pygame.time.Clock
        self._delta: int

    def init(self):
        self._clock = pygame.time.Clock()

    def tick(self):
        fps = GameConfig.instance().fps
        self._delta = self._clock.tick(fps)

    def delta(self) -> int:
        return self._delta
    
    def delta_sec(self) -> float:
        return self._delta / SECOND_MS


class Timer:

    def __init__(self, ms_: int):
        self._ms = ms_
        self._start = 0
        self._is_activated = False

    def _time_ms(self) -> int:
        return time.time_ns() // SECOND_NS

    def start(self):
        self._is_activated = True
        self._start = self._time_ms()

    def stop(self):
        self._is_activated = False

    def remain(self):
        elapsed_time = self._time_ms() - self._start
        return self._ms - elapsed_time

    def over(self) -> bool:
        return self._is_activated and self.remain() <= 0
