import unittest
from random import Random

from snake_game.logic import DOWN, LEFT, RIGHT, UP, GameConfig, GameState, SnakeGame


class SnakeGameTests(unittest.TestCase):
    def make_game(self, food=(5, 2)):
        return SnakeGame(GameConfig(width=8, height=6), Random(1), food=food)

    def test_moves_forward_without_growing(self):
        game = self.make_game()

        state = game.step()

        self.assertEqual(state.snake, ((5, 3), (4, 3), (3, 3)))
        self.assertEqual(state.score, 0)
        self.assertEqual(state.food, (5, 2))
        self.assertFalse(state.game_over)

    def test_grows_and_scores_when_eating_food(self):
        game = self.make_game(food=(5, 3))

        state = game.step()

        self.assertEqual(state.snake, ((5, 3), (4, 3), (3, 3), (2, 3)))
        self.assertEqual(state.score, 1)
        self.assertNotIn(state.food, state.snake)
        self.assertFalse(state.game_over)

    def test_rejects_immediate_reverse_direction(self):
        game = self.make_game()

        state = game.step(LEFT)

        self.assertEqual(state.direction, RIGHT)
        self.assertEqual(state.snake[0], (5, 3))
        self.assertFalse(state.game_over)

    def test_wall_collision_ends_game(self):
        game = SnakeGame(GameConfig(width=5, height=5), Random(1), food=(0, 0))
        game.state = GameState(snake=((4, 2), (3, 2), (2, 2)), direction=RIGHT, food=(0, 0))

        state = game.step()

        self.assertTrue(state.game_over)
        self.assertEqual(state.score, 0)

    def test_self_collision_ends_game(self):
        game = SnakeGame(GameConfig(width=7, height=7), Random(1), food=(0, 0))
        game.state = GameState(
            snake=((3, 3), (3, 4), (2, 4), (2, 3), (2, 2), (3, 2)),
            direction=LEFT,
            food=(0, 0),
        )

        state = game.step(DOWN)

        self.assertTrue(state.game_over)

    def test_moving_into_vacated_tail_is_allowed(self):
        game = SnakeGame(GameConfig(width=7, height=7), Random(1), food=(0, 0))
        game.state = GameState(
            snake=((3, 3), (3, 4), (2, 4), (2, 3)),
            direction=LEFT,
            food=(0, 0),
        )

        state = game.step()

        self.assertEqual(state.snake, ((2, 3), (3, 3), (3, 4), (2, 4)))
        self.assertFalse(state.game_over)

    def test_food_spawn_does_not_overlap_snake(self):
        game = self.make_game(food=(5, 3))

        state = game.step()

        self.assertNotIn(state.food, state.snake)
        self.assertGreaterEqual(state.food[0], 0)
        self.assertLess(state.food[0], game.config.width)
        self.assertGreaterEqual(state.food[1], 0)
        self.assertLess(state.food[1], game.config.height)


if __name__ == "__main__":
    unittest.main()
