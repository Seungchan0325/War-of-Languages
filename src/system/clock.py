from time import time_ns

from pygame.time import Clock as PygameClock

from common import SingletonInstane
from game_config import GameConfig

SECOND_MS = 1000
NS_TO_MS = 1000000
SECOND_NS = 1000000000


class Clock(SingletonInstane):

    def __init__(self):
        self._clock: PygameClock
        self._delta: int

    def init(self):

        self._clock = PygameClock()

    def tick(self):
        fps = GameConfig.instance().fps
        self._delta = self._clock.tick(fps)

    def fps(self):
        return self._clock.get_fps()

    def delta_sec(self) -> float:
        # # 파이썬이 구려서 그냥 상수씀 ㅅㄱ
        fps = GameConfig.instance().fps
        return 1 / fps


class Timer:

    def __init__(self, ms_: int):
        self._ms = ms_
        self._start = 0
        self._is_activate = False

    def _time_ms(self) -> int:
        # Convert nanosecond to millisecond
        return time_ns() // NS_TO_MS

    def start(self):
        self._is_activate = True
        self._start = self._time_ms()

    def stop(self):
        self._is_activate = False

    def remain(self):
        delta_time = self._time_ms() - self._start
        return self._ms - delta_time

    def over(self) -> bool:
        return self._is_activate and self.remain() <= 0
