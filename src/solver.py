from math import inf

from pydantic import config

from src.classes.Models import Hub, MapConfig, ZoneType, TurnState


class Solver:
    def _entry_cost(self, hub: Hub) -> int:
        if hub.zone == ZoneType.BLOCKED:
            return 100000
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
        drones: list[int] = []

        steps: list[TurnState] = []

        turn_state = TurnState()
        for i in range(1, nb_drones + 1):
            drones.append(i)
            turn_state.add_drone_state(i, map_config.start_hub)

        steps.append(turn_state)

        while True:
            turn_state = TurnState()
            for drone in drones:
                if steps[-1].get_hub_by_drone_id(drone) == map_config.end_hub:
                    turn_state.add_drone_state(drone, map_config.end_hub)
                    continue

                current_hub = steps[-1].get_hub_by_drone_id(drone)
                current_distance = end_distance_map[current_hub]

                if current_hub is None:
                    raise Exception(f"Drone {drone} has no current hub")

                adj_goal = dict(
                    sorted(
                        {
                            hub: end_distance_map[hub]
                            for hub in adjacency[current_hub]
                            if hub in end_distance_map
                        }.items(),
                        key=lambda item: item[1],
                    )
                )
                hub_to_get: str | None = None

                if len(steps) > 1:
                    last_hub = map_config.get_hub_by_name(
                        steps[-1].get_hub_by_drone_id(drone)
                    )
                    previous_hub = map_config.get_hub_by_name(
                        steps[-2].get_hub_by_drone_id(drone)
                    )
                    if (
                        last_hub is not None
                        and last_hub.zone == ZoneType.RESTRICTED
                        and previous_hub is not None
                        and previous_hub.zone != ZoneType.RESTRICTED
                    ):
                        turn_state.add_drone_state(
                            drone, steps[-1].get_hub_by_drone_id(drone)
                        )
                        continue

                for hub in adj_goal:

                    hub_obj = map_config.get_hub_by_name(hub)

                    drone_per_hub: dict[str, int] = (
                        turn_state.get_drone_count_per_hub()
                    )

                    if hub_obj is None:
                        continue

                    if (
                        hub_obj.zone == ZoneType.PRIORITY
                        and drone_per_hub.get(hub, 0) < hub_obj.max_drones
                        and end_distance_map[hub] < current_distance
                    ) or hub == map_config.end_hub:
                        hub_to_get = hub
                        break

                    if (
                        (
                            (
                                hub_obj.zone == ZoneType.NORMAL
                                or hub_obj.zone == ZoneType.RESTRICTED
                            )
                            and end_distance_map[hub] < current_distance
                        )
                        and drone_per_hub.get(hub, 0) < hub_obj.max_drones
                        and hub_to_get is None
                    ):
                        hub_to_get = hub

                if hub_to_get is None:
                    hub_to_get = steps[-1].get_hub_by_drone_id(drone)
                turn_state.add_drone_state(drone, hub_to_get)
            steps.append(turn_state)

            if all(
                drone_state.at_hub == map_config.end_hub
                for drone_state in turn_state.drones_state
            ):
                return steps


def _solve_maps(maps: dict[str, MapConfig]) -> dict[str, list[TurnState]]:
    solver = Solver()
    solved_maps: dict[str, list[TurnState]] = {}
    for map_name, map in maps.items():
        dist_map = solver._build_end_distance_map(map_name, map)

        steps = solver.get_drone_steps(map, dist_map)
        print(f"{map_name} (len: {len(steps)})\n\n")
        solved_maps[map_name] = steps
    return solved_maps
