from pathlib import Path
from json import dumps

from src.classes.Models import MapConfig

from .parser import MapParser
from .solver import Solver
from .classes.Exceptions import ParseError

from sys import argv

from src import solver


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
            print(file)
            maps[file.name] = parser.parse_file(file)
        print(maps)
        print()
        print()
        solver = Solver(maps)
        for map_name, map in solver.maps.items():
            print(dumps(solver._build_end_distance_map(map)))
            print()
        return 0
    except ParseError as err:
        print(f"Parsing error: {err}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
