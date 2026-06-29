from dataclasses import dataclass
from enum import Enum
from typing import Self
from pydantic import BaseModel, Field


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
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

    def get_hub_by_drone_id(self, drone_id: int) -> str:
        for drone in self.drones_state:
            if drone.drone_id == drone_id:
                return drone.at_hub

    def get_already_takken_hubs(self) -> list[str]:
        return [drone_state.at_hub for drone_state in self.drones_state]

    def get_drone_count_per_hub(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for drone_state in self.drones_state:
            counts[drone_state.at_hub] = counts.get(drone_state.at_hub, 0) + 1
        return counts
