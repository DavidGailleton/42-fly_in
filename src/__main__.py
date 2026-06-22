from pathlib import Path

from src.classes.Models import MapConfig

from .parser import MapParser
from .classes.Exceptions import ParseError

from sys import argv


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
        return 0
    except ParseError as err:
        print(f"Parsing error: {err}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
