import os
from pathlib import Path
import sys

from src.classes.Models import MapConfig, TurnState

from .parser import MapParser
from .solver import _solve_maps
from .classes.Exceptions import ParseError

from sys import argv
from .display import PyGameDisplayer


def print_moves(steps: list[TurnState]) -> None:
    pass


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
            displayer = PyGameDisplayer(
                maps[no_maps[res]], solved_maps[no_maps[res]]
            )
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
        return 0
    except ParseError as err:
        print(f"Parsing error: {err}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
