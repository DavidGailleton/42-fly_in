from enum import Enum
from pydantic import BaseModel, Field
from numpy import ndarray, uint32, str_
import numpy.typing as npt


class ZoneType(Enum):
    NORMAL = 0
    BLOCKED = 1
    RESTRICTED = 2
    PRIORITY = 3


class Hub(BaseModel):
    name: str_
    coordinate: tuple[uint32, uint32]
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str_ | None = Field(default=None)
    max_drones: uint32 = Field(default=uint32(1))


class Connection(BaseModel):
    hubs: tuple[Hub, Hub]
    max_link_capacity: uint32 = Field(default=uint32(1))


class Config(BaseModel):
    nb_drones: uint32
    start_hub: Hub
    end_hub: Hub
    hubs: npt.NDArray
    connections: npt.NDArray


def line_to_hub(line: str) -> Hub:
    hub = {
        "name": line.split(" ")[1],
        "coordinate": (uint32(line.split(" ")[2]), uint32(line.split(" ")[3])),
    }
    if len(line.split(" ")) > 4:
        try:
            metadata = line[line.index("[") + 1 : line.index("]")].split(" ")
            for data in metadata:
                if data.startswith("color="):
                    if "color" in hub.keys():
                        raise Exception(
                            f'"color" key is defined multiple time in {line}'
                        )
                    if data.removeprefix("color=") == "":
                        raise Exception(f'"color" value not defined in {line}')
                    hub["color"] = data.removeprefix("color=")
                elif data.startswith("zone="):
                    if "zone" in hub.keys():
                        raise Exception(
                            f'"zone" key is defined multiple time in {line}'
                        )
                    if data.removeprefix("zone=") == "":
                        raise Exception(f'"zone" value not defined in {line}')
                    hub["zone"] = ZoneType(
                        data.removeprefix("zone=").capitalize()
                    )
                elif data.startswith("max_drones="):
                    if "max_drones" in hub.keys():
                        raise Exception(
                            f'"max_drones" key is defined multiple time in {line}'
                        )
                    if data.removeprefix("max_drones=") == "":
                        raise Exception(
                            f'"max_drones" value not defined in {line}'
                        )
                    hub["max_drones"] = uint32(
                        data.removeprefix("max_drones=")
                    )
                else:
                    raise Exception(
                        f"Invalid key=value format or unknown key for {data} in line {line}"
                    )
        except ValueError:
            raise Exception(f"Invalid format in line : {line}")
    return Hub(**hub)


def line_to_connection(line: str) -> Connection:
    hub_one = 
    connection = {"hubs": (line.split(" ")[1], line.split(" ")[2])}

    return Connection(**connection)


def parsing(file: str_):
    with open(file) as content:
        i: uint32 = uint32(0)
        config: dict[str, list[Hub] | list[Connection] | uint32 | Hub] = {
            "hubs": [],
            "connections": [],
        }
        for line in content:
            if line.startswith("#") or line == "":
                continue
            if i == 0 and not line.startswith("nb_drones: "):
                raise Exception("First line should be nb_drones")

            if line.startswith("nb_drones: "):
                try:
                    config["nb_drones"]
                    raise Exception("nb_drones is defined multiple time")
                except KeyError:
                    config["nb_drones"] = uint32(
                        line.removeprefix("nb_drones: ")
                    )
            elif line.startswith("start_hub: "):
                pass
            elif line.startswith("end_hub: "):
                pass
            elif line.startswith("hub: "):
                pass
            elif line.startswith("connection: "):
                pass
