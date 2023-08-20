import dataclasses

from common import SingletonInstane


@dataclasses.dataclass
class GameConfig(SingletonInstane):

    def __init__(self):
        self.name: str = "War of Languages"
        self.fps: int = 30
