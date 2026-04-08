"""Deterministic core rules for a classic Snake game."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable, Optional

Coord = tuple[int, int]

UP: Coord = (0, -1)
DOWN: Coord = (0, 1)
LEFT: Coord = (-1, 0)
RIGHT: Coord = (1, 0)

DIRECTIONS: dict[str, Coord] = {
    "up": UP,
    "down": DOWN,
    "left": LEFT,
    "right": RIGHT,
}


@dataclass(frozen=True)
class GameConfig:
    width: int = 20
    height: int = 20
    initial_length: int = 3
    initial_direction: Coord = RIGHT

    def __post_init__(self) -> None:
        if self.width < self.initial_length + 1:
            raise ValueError("width must fit the initial snake and at least one food cell")
        if self.height < 2:
            raise ValueError("height must be at least 2")
        if self.initial_direction not in DIRECTIONS.values():
            raise ValueError("initial_direction must be one of the direction constants")


@dataclass(frozen=True)
class GameState:
    snake: tuple[Coord, ...]
    direction: Coord
    food: Coord
    score: int = 0
    game_over: bool = False


def opposite(first: Coord, second: Coord) -> bool:
    return first[0] + second[0] == 0 and first[1] + second[1] == 0


class SnakeGame:
    """Classic Snake rules with no UI concerns."""

    def __init__(
        self,
        config: Optional[GameConfig] = None,
        rng: Optional[Random] = None,
        *,
        food: Optional[Coord] = None,
    ) -> None:
        self.config = config or GameConfig()
        self.rng = rng or Random()
        self.state = self._initial_state(food=food)

    def restart(self, *, food: Optional[Coord] = None) -> GameState:
        self.state = self._initial_state(food=food)
        return self.state

    def change_direction(self, direction: Coord) -> GameState:
        if direction not in DIRECTIONS.values():
            raise ValueError("direction must be one of the direction constants")
        if not opposite(self.state.direction, direction):
            self.state = GameState(
                snake=self.state.snake,
                direction=direction,
                food=self.state.food,
                score=self.state.score,
                game_over=self.state.game_over,
            )
        return self.state

    def step(self, direction: Optional[Coord] = None) -> GameState:
        if self.state.game_over:
            return self.state
        if direction is not None:
            self.change_direction(direction)

        head = self.state.snake[0]
        next_head = (
            head[0] + self.state.direction[0],
            head[1] + self.state.direction[1],
        )
        grows = next_head == self.state.food

        if not self._inside_grid(next_head):
            self.state = self._with_game_over()
            return self.state

        body_to_check = self.state.snake if grows else self.state.snake[:-1]
        if next_head in body_to_check:
            self.state = self._with_game_over()
            return self.state

        next_snake = (next_head,) + self.state.snake if grows else (next_head,) + self.state.snake[:-1]
        next_score = self.state.score + 1 if grows else self.state.score
        next_food = self._spawn_food(next_snake) if grows else self.state.food

        self.state = GameState(
            snake=next_snake,
            direction=self.state.direction,
            food=next_food,
            score=next_score,
            game_over=False,
        )
        return self.state

    def _initial_state(self, *, food: Optional[Coord]) -> GameState:
        y = self.config.height // 2
        start_x = self.config.width // 2
        snake = tuple((start_x - offset, y) for offset in range(self.config.initial_length))
        if food is None:
            food = self._spawn_food(snake)
        self._validate_food(food, snake)
        return GameState(
            snake=snake,
            direction=self.config.initial_direction,
            food=food,
        )

    def _spawn_food(self, snake: Iterable[Coord]) -> Coord:
        occupied = set(snake)
        free_cells = [
            (x, y)
            for y in range(self.config.height)
            for x in range(self.config.width)
            if (x, y) not in occupied
        ]
        if not free_cells:
            return (-1, -1)
        return self.rng.choice(free_cells)

    def _validate_food(self, food: Coord, snake: Iterable[Coord]) -> None:
        if not self._inside_grid(food):
            raise ValueError("food must be inside the grid")
        if food in set(snake):
            raise ValueError("food must not overlap the snake")

    def _inside_grid(self, coord: Coord) -> bool:
        return 0 <= coord[0] < self.config.width and 0 <= coord[1] < self.config.height

    def _with_game_over(self) -> GameState:
        return GameState(
            snake=self.state.snake,
            direction=self.state.direction,
            food=self.state.food,
            score=self.state.score,
            game_over=True,
        )

