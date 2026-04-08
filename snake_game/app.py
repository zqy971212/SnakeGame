"""Minimal Tkinter UI for the classic Snake game."""

from __future__ import annotations

import tkinter as tk
from typing import Optional

from .logic import DOWN, LEFT, RIGHT, UP, Coord, GameConfig, SnakeGame

CELL_SIZE = 24
TICK_MS = 140


class SnakeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.game = SnakeGame(GameConfig(width=20, height=20))
        self.pending_direction: Optional[Coord] = None
        self.paused = False

        root.title("Snake")
        root.resizable(False, False)

        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 12))
        self.score_label.pack(padx=8, pady=(8, 4))

        self.canvas = tk.Canvas(
            root,
            width=self.game.config.width * CELL_SIZE,
            height=self.game.config.height * CELL_SIZE,
            background="#f4f4f4",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.canvas.pack(padx=8, pady=4)

        self.status_label = tk.Label(root, text="Use arrows or WASD.", font=("Arial", 10))
        self.status_label.pack(padx=8, pady=4)

        controls = tk.Frame(root)
        controls.pack(padx=8, pady=(4, 8))
        tk.Button(controls, text="Up", width=8, command=lambda: self.queue_direction(UP)).grid(row=0, column=1)
        tk.Button(controls, text="Left", width=8, command=lambda: self.queue_direction(LEFT)).grid(row=1, column=0)
        tk.Button(controls, text="Restart", width=8, command=self.restart).grid(row=1, column=1)
        tk.Button(controls, text="Right", width=8, command=lambda: self.queue_direction(RIGHT)).grid(row=1, column=2)
        tk.Button(controls, text="Down", width=8, command=lambda: self.queue_direction(DOWN)).grid(row=2, column=1)
        self.pause_button = tk.Button(controls, text="Pause", width=8, command=self.toggle_pause)
        self.pause_button.grid(row=3, column=1)

        for key, direction in {
            "<Up>": UP,
            "w": UP,
            "W": UP,
            "<Down>": DOWN,
            "s": DOWN,
            "S": DOWN,
            "<Left>": LEFT,
            "a": LEFT,
            "A": LEFT,
            "<Right>": RIGHT,
            "d": RIGHT,
            "D": RIGHT,
        }.items():
            root.bind(key, lambda event, direction=direction: self.queue_direction(direction))
        root.bind("<space>", lambda event: self.restart())
        root.bind("p", lambda event: self.toggle_pause())
        root.bind("P", lambda event: self.toggle_pause())
        root.bind("r", lambda event: self.restart())
        root.bind("R", lambda event: self.restart())

        self.draw()
        self.root.after(TICK_MS, self.tick)

    def queue_direction(self, direction: Coord) -> None:
        self.pending_direction = direction

    def restart(self) -> None:
        self.game.restart()
        self.pending_direction = None
        self.paused = False
        self.pause_button.config(text="Pause")
        self.status_label.config(text="Use arrows or WASD.")
        self.draw()

    def toggle_pause(self) -> None:
        if self.game.state.game_over:
            return
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        self.status_label.config(text="Paused. Press P to resume." if self.paused else "Use arrows or WASD.")

    def tick(self) -> None:
        if not self.paused:
            self.game.step(self.pending_direction)
            self.pending_direction = None
        self.draw()
        if self.game.state.game_over:
            self.status_label.config(text="Game over. Press Restart, Space, or R.")
        self.root.after(TICK_MS, self.tick)

    def draw(self) -> None:
        self.canvas.delete("all")
        state = self.game.state
        self.score_label.config(text=f"Score: {state.score}")

        for x in range(self.game.config.width):
            for y in range(self.game.config.height):
                x1 = x * CELL_SIZE
                y1 = y * CELL_SIZE
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + CELL_SIZE,
                    y1 + CELL_SIZE,
                    outline="#dddddd",
                    fill="#f4f4f4",
                )

        food_x, food_y = state.food
        if food_x >= 0:
            self._draw_cell(food_x, food_y, "#c0392b")

        for index, (x, y) in enumerate(state.snake):
            self._draw_cell(x, y, "#1f6f43" if index == 0 else "#2e8b57")

    def _draw_cell(self, x: int, y: int, color: str) -> None:
        inset = 2
        x1 = x * CELL_SIZE + inset
        y1 = y * CELL_SIZE + inset
        self.canvas.create_rectangle(
            x1,
            y1,
            x1 + CELL_SIZE - inset * 2,
            y1 + CELL_SIZE - inset * 2,
            fill=color,
            outline=color,
        )


def main() -> None:
    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
