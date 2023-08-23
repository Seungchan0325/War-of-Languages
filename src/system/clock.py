import time

import pygame

from common import SingletonInstane
from game_config import GameConfig


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


class Timer:

    def __init__(self, ms_: int):
        self._ms = ms_
        self._start = 0

    def _time_ms(self) -> int:
        return time.time_ns() // 1_000_000

    def start(self):
        self._start = self._time_ms()

    def remain(self):
        elapsed_time = self._time_ms() - self._start
        return self._ms - elapsed_time

    def over(self) -> bool:
        return 0 >= self.remain()
