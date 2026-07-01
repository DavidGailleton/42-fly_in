import os
from pathlib import Path
import sys

from src.classes.Models import MapConfig, TurnState, ZoneType

from .parser import MapParser
from .solver import _solve_maps
from .classes.Exceptions import ParseError

from sys import argv
from .display import PyGameDisplayer


def print_moves(map: MapConfig, steps: list[TurnState]) -> None:
    for i in range(len(steps)):
        if i == 0:
            continue
        for drone_state in steps[i].drones_state:
            if map.get_hub_by_name(drone_state.at_hub) is None:
                raise Exception(f"Unknown hub {drone_state.at_hub}")
            if (
                map.get_hub_by_name(drone_state.at_hub).zone
                == ZoneType.RESTRICTED
                and steps[i - 1].get_hub_by_drone_id(drone_state.drone_id)
                != drone_state.at_hub
            ):
                # Update connection name
                print(f"D{drone_state.drone_id}-corridor", end=" ")
            elif (
                i > 1
                and map.get_hub_by_name(drone_state.at_hub).zone
                == ZoneType.RESTRICTED
                and steps[i - 1].get_hub_by_drone_id(drone_state.drone_id)
                == drone_state.at_hub
                and drone_state.at_hub
                != steps[i - 2].get_hub_by_drone_id(drone_state.drone_id)
            ):
                print(f"D{drone_state.drone_id}-{drone_state.at_hub}", end=" ")
            elif drone_state.at_hub != steps[i - 1].get_hub_by_drone_id(
                drone_state.drone_id
            ):
                print(f"D{drone_state.drone_id}-{drone_state.at_hub}", end=" ")
        print()


def start_program(
    maps: dict[str, MapConfig], solved_maps: dict[str, list[TurnState]]
) -> None:
    no_maps: dict[int, str] = {
        (i + 1): map_name
        for i, map_name in zip(range(len(maps)), list(maps.keys()))
    }

    os.system("cls" if sys.__name__ == "nt" else "clear")

    while True:
        try:
            print("Choose one map:")
            for n, map_name in no_maps.items():
                print(f"\t- {map_name} ({n})")
            print(f"\t- Exit ({len(no_maps) + 1})")
            res = int(input("\nmap id: "))
            if res == len(no_maps) + 1:
                return
            map = maps[no_maps[res]]
            solved_map = solved_maps[no_maps[res]]
            displayer = PyGameDisplayer(map, solved_map)
            print_moves(map, solved_map)
            displayer.start_player()
        except (ValueError, KeyError):
            print("Invalid key")


def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    parser = MapParser()
    maps: dict[str, MapConfig] = {}
    try:
        files = Path(argv[1]).rglob("*.txt")
        for file in files:
            maps[file.name] = parser.parse_file(file)
        solved_maps = _solve_maps(maps)
        start_program(maps, solved_maps)
        return 0
    except ParseError as err:
        print(f"Parsing error: {err}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
