from src.classes.Models import MapConfig


class Solver:
    def __init__(self, maps: dict[str, MapConfig]) -> None:
        self.maps = maps
        self._solved_maps = []

    def _solve_maps(self) -> None: ...
