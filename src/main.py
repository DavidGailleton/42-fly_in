from .parsing import Parsing


def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    try:
        parser = Parsing()
        map = parser.get_map_data("maps/easy/01_linear_path.txt")
        print(map)
        print("Fly-In".index("t"))
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
