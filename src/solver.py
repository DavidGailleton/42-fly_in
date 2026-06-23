from math import inf

from pydantic import config

from src.classes.Models import Hub, MapConfig, ZoneType, TurnState


class Solver:

    def _entry_cost(self, hub: Hub) -> int:
        if hub.zone == ZoneType.BLOCKED:
            return -1
        if hub.zone == ZoneType.RESTRICTED:
            return 2
        return 1

    def _build_end_distance_map(
        self, map_name: str, map_config: MapConfig
    ) -> dict[str, int]:
        hubs_by_name: dict[str, Hub] = {
            hub.name: hub for hub in map_config.hubs
        }

        adjacency: dict[str, list[str]] = {
            hub.name: [] for hub in map_config.hubs
        }
        for connection in map_config.connections:
            hub_a, hub_b = connection.hubs
            adjacency[hub_a].append(hub_b)
            adjacency[hub_b].append(hub_a)

        distances: dict[str, float] = {
            hub.name: inf for hub in map_config.hubs
        }
        distances[map_config.end_hub] = 0

        unvisited: set[str] = set(hubs_by_name.keys())

        while unvisited:
            current = min(unvisited, key=lambda hub_name: distances[hub_name])

            if distances[current] == inf:
                break

            unvisited.remove(current)

            current_hub = hubs_by_name[current]
            if current_hub.zone == ZoneType.BLOCKED:
                continue

            for neighbor in adjacency[current]:
                if neighbor not in unvisited:
                    continue

                neighbor_hub = hubs_by_name[neighbor]
                if neighbor_hub.zone == ZoneType.BLOCKED:
                    continue

                candidate = distances[current] + self._entry_cost(current_hub)

                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate

        res = {
            hub_name: int(distance)
            for hub_name, distance in distances.items()
            if distance != inf
        }
        if map_config.start_hub not in [hub_name for hub_name in res]:
            raise Exception(f"path not found for {map_name}")
        return res

    def get_drone_steps(
        self, map_config: MapConfig, end_distance_map: dict[str, int]
    ):
        hubs_by_name: dict[str, Hub] = {
            hub.name: hub for hub in map_config.hubs
        }

        adjacency: dict[str, list[str]] = {
            hub.name: [] for hub in map_config.hubs
        }

        for connection in map_config.connections:
            hub_a, hub_b = connection.hubs
            adjacency[hub_a].append(hub_b)
            adjacency[hub_b].append(hub_a)

        nb_drones = map_config.nb_drones
        i = 1
        drones: dict[int, str] = {}

        while i < nb_drones:
            drones[i] = map_config.start_hub
            i += 1

        steps: list[TurnState] = []

        while True:
            turn_state = TurnState()
            for drone, pos in drones.items():
                adj_goal = dict(
                    sorted(
                        {
                            hub: end_distance_map[hub]
                            for hub in adjacency
                            if hub in end_distance_map
                        }.items()
                    )
                )
                for hub in adj_goal:
                    if (
                        map_config.get_hub_by_name(hub) is Hub
                        and map_config.get_hub_by_name(hub)
                        == ZoneType.PRIORITY
                    ):
                        ...


def _solve_maps(maps: dict[str, MapConfig]):
    solver = Solver()
    for map_name, map in maps.items():
        dist_map = solver._build_end_distance_map(map_name, map)
