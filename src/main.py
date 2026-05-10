def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    try:
        print("Fly-In")
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
