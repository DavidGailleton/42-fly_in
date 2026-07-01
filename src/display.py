from abc import ABC, abstractmethod

from pygame import Color, Surface, SurfaceType, draw

import pygame
from .classes.Models import Colors, MapConfig, TurnState


class Displayer(ABC):
    def __init__(
        self, map_config: MapConfig, drone_steps: list[TurnState]
    ) -> None:
        self.map_config = map_config
        self.drone_steps = drone_steps

    @abstractmethod
    def start_player(self) -> None:
        pass


class PyGameDisplayer(Displayer):
    def __init__(
        self,
        map_config: MapConfig,
        drone_steps: list[TurnState],
    ) -> None:
        super().__init__(map_config, drone_steps)

    def set_base_surface(self, surface: Surface) -> None:
        screen_width, screen_height = surface.get_size()
        margin = 80

        x_values = [hub.coordinate[0] for hub in self.map_config.hubs]
        y_values = [hub.coordinate[1] for hub in self.map_config.hubs]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        range_x = max(1, max_x - min_x)
        range_y = max(1, max_y - min_y)

        usable_width = screen_width - 2 * margin
        usable_height = screen_height - 2 * margin

        scale_x = usable_width / range_x
        scale_y = usable_height / range_y

        hub_radius = max(8, min(20, int(min(scale_x, scale_y) / 4)))

        def to_screen(coord: tuple[int, int]) -> tuple[int, int]:
            x, y = coord
            screen_x = margin + int((x - min_x) * scale_x)
            screen_y = margin + int((y - min_y) * scale_y)
            return (screen_x, screen_y)

        surface.fill(Colors.WHITE.value)

        for connection in self.map_config.connections:
            hub_0 = self.map_config.get_hub_by_name(connection.hubs[0])
            hub_1 = self.map_config.get_hub_by_name(connection.hubs[1])

            if hub_0 is None or hub_1 is None:
                raise Exception("Error during connection display")

            draw.line(
                surface,
                Colors.BLACK.value,
                to_screen(hub_0.coordinate),
                to_screen(hub_1.coordinate),
                2,
            )

        for hub in self.map_config.hubs:
            draw.circle(
                surface,
                hub.color.value,
                to_screen(hub.coordinate),
                hub_radius,
            )

    def start_player(self) -> None:
        try:
            pygame.init()
            screen = pygame.display.set_mode((1920, 1080))
            clock = pygame.time.Clock()
            running = True

            n_frame = 0

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                self.set_base_surface(screen)

                pygame.display.flip()

                clock.tick(30)

                n_frame += 1

        except Exception as err:
            print(err)

        finally:
            pygame.quit()
