from enum import Enum
import re
from pydantic import BaseModel, Field


class ZoneType(Enum):
    NORMAL = 0
    BLOCKED = 1
    RESTRICTED = 2
    PRIORITY = 3


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1)


class Connection(BaseModel):
    hubs: tuple[Hub, Hub]
    max_link_capacity: int = Field(default=1)


class MapConfig(BaseModel):
    nb_drones: int
    start_hub: str
    end_hub: str
    hubs: list[Hub]
    connections: list[Connection]


class Parsing:
    def get_metadata(self, line: str) -> dict[str, str | int | ZoneType]:
        res: dict[str, str | int | ZoneType] = {}
        params = re.findall("[*]", line)
        if len(params) > 1:
            raise ValueError("Multiple metadata definition")
        if len(params) == 0:
            return {}
        av_args = {"color", "max_drones", "max_link_capacity", "zone"}
        for param in params[0].removeprefix("[").removesuffix("]").split(" "):
            k, v = param.split("=", 1)
            if k not in av_args:
                raise ValueError(f"Unknown key {k}")
            if k in list(res.keys()):
                raise ValueError(f"Multiple definition of {k}")
            if k == "zone":
                match v:
                    case "normal":
                        v = ZoneType.NORMAL
                    case "blocked":
                        v = ZoneType.BLOCKED
                    case "restricted":
                        v = ZoneType.RESTRICTED
                    case "priority":
                        v = ZoneType.PRIORITY
                    case _:
                        raise ValueError(f"Unknown zone type : {v}")
            res[k] = v
        return res

    def hub_from_line(self, line: str, act_config: dict) -> Hub:
        settings = line.split(" ")
        new_hub: dict = {}
        new_hub["name"] = settings[1]
        for hub in act_config["hubs"]:
            if isinstance(hub, Hub):
                if hub.name == new_hub["name"]:
                    raise ValueError("Duplicate hubs name")
        new_hub["coordinate"] = (int(settings[2]), int(settings[3]))
        new_hub = new_hub | self.get_metadata(line)
        return Hub(**new_hub)

    def connection_from_line(self, line: str, act_config: dict) -> Connection:
        hub1, hub2 = line.split()[1].split("-", 1)
        rhub1, rhub2 = None, None
        for hub in act_config["hubs"]:
            if rhub1 is None and hub.name == hub1:
                rhub1 = hub
            if rhub2 is None and hub.name == hub2:
                rhub2 = hub
        if rhub1 is None:
            raise ValueError(f"Unknown hub {hub1}")
        if rhub2 is None:
            raise ValueError(f"Unknown hub {hub2}")
        connection: dict = {
            "hubs": (min([rhub1, rhub2]), max([rhub1, rhub2]))
        } | self.get_metadata(line)
        for con in act_config["connections"]:
            if con.hubs == connection["hubs"]:
                raise ValueError("Duplicate connection hubs")
        return Connection(**connection)

    def get_map_data(self, file: str) -> MapConfig | None:
        with open(file) as content:
            config: dict[str, str | list[Hub] | list[Connection] | int] = {
                "hubs": [],
                "connections": [],
            }
            i = 0
            for n_line, line in enumerate(content):
                try:
                    if line.strip().startswith("#") or line.strip() == "":
                        continue
                    if i == 0 and not line.startswith("nb_drones: "):
                        raise ValueError("First line should be nb_drones")

                    if line.startswith("nb_drones:"):
                        if config.get("nb_drones") is None:
                            config["nb_drones"] = int(
                                line.removeprefix("nb_drones: ")
                            )
                        else:
                            raise ValueError(
                                "Multiple definition of nb_drones"
                            )
                    elif (
                        line.startswith("start_hub:")
                        or line.startswith("end_hub:")
                        or line.startswith("hub:")
                    ):
                        new_hub = self.hub_from_line(line, config)
                        if line.startswith("start_hub:"):
                            if config.get("start_hub") is None:
                                raise ValueError(
                                    "Multiple definition of start_hub"
                                )
                            config["start_hub"] = new_hub.name
                        elif line.startswith("end_hub:"):
                            if config.get("end_hub") is None:
                                raise ValueError(
                                    "Multiple definition of end_hub"
                                )
                            config["end_hub"] = new_hub.name
                        if isinstance(config["hubs"], list):
                            config["hubs"].append(new_hub)
                    elif line.startswith("connection: "):
                        if isinstance(config["connections"], list):
                            config["connections"].append(
                                self.connection_from_line(line, config)
                            )
                    i += 1
                except Exception as err:
                    print(f"Line {n_line}: {line}\nError: {err}")
                    return None
        return MapConfig(**config)
