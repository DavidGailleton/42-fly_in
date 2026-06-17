from enum import Enum
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
