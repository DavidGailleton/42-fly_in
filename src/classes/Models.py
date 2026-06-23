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
