from abc import ABC, abstractmethod

import pygame
from .classes.Models import MapConfig, TurnState


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
        self, map_config: MapConfig, drone_steps: list[TurnState]
    ) -> None:
        super().__init__(map_config, drone_steps)

    def start_player(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((1920, 1080))
        clock = pygame.time.Clock()
        running = True

        n_frame = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill("white")

            pygame.display.flip()

            clock.tick(30)

            n_frame += 1
