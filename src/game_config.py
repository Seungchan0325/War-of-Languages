import dataclasses

from common import SingletonInstane


@dataclasses.dataclass(frozen=True)
class GameConfig(SingletonInstane):
    name: str = "War of Languages"
    fps: int = 30
