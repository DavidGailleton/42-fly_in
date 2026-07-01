from dataclasses import dataclass
from enum import Enum
from typing import Self
from pydantic import BaseModel, Field


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Colors(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (127, 127, 127)
    PURPLE = (128, 0, 128)
    BROWN = (165, 42, 42)
    ORANGE = (255, 165, 0)
    MAROON = (128, 0, 0)
    GOLD = (255, 215, 0)
    DARKRED = (139, 0, 0)
    VIOLET = (238, 130, 238)
    CRIMSON = (220, 20, 60)
    RAINBOW = (255, 255, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    LIME = (50, 205, 50)
    MAGENTA = (255, 0, 255)


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: Colors = Field(default=Colors.RED)
    max_drones: int = Field(default=1)


class Connection(BaseModel):
    hubs: tuple[str, str]
    max_link_capacity: int = Field(default=1)


class MapConfig(BaseModel):
    nb_drones: int
    start_hub: str
    end_hub: str
    hubs: list[Hub]
    connections: list[Connection]

    def get_hub_by_name(self, name: str) -> Hub | None:
        for hub in self.hubs:
            if hub.name == name:
                return hub
        return None


class TurnState:
    @dataclass
    class DroneState:
        drone_id: int
        at_hub: str

    def __init__(self) -> None:
        self.drones_state = []

    def add_drone_state(self, drone_id: int, at_hub: str) -> None:
        self.drones_state.append(self.DroneState(drone_id, at_hub))

    def get_hub_by_drone_id(self, drone_id: int) -> str | None:
        for drone in self.drones_state:
            if drone.drone_id == drone_id:
                return drone.at_hub
        return None

    def get_already_takken_hubs(self) -> list[str]:
        return [drone_state.at_hub for drone_state in self.drones_state]

    def get_drone_count_per_hub(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for drone_state in self.drones_state:
            counts[drone_state.at_hub] = counts.get(drone_state.at_hub, 0) + 1
        return counts
