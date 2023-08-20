import dataclasses


@dataclasses.dataclass
class GameConfig:
    
    name: str = "War of Languages"
    fps: int = 30
