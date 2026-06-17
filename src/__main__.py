from .parser import MapParser
from .classes.Exceptions import ParseError


def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    parser = MapParser()
    try:
        config = parser.parse_file("maps/easy/01_linear_path.txt")
        print(config.model_dump())
        return 0
    except ParseError as err:
        print(f"Parsing error: {err}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
