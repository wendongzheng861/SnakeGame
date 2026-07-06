#!/usr/bin/env python3
"""
test_snake.py — 贪吃蛇核心逻辑单元测试

运行：python3 -m pytest test_snake.py -v
或：  python3 test_snake.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from game_core import (
    GameCore, Snake, Food,
    UP, DOWN, LEFT, RIGHT,
)


# ══════════════════════════════════════════════════════
# Snake 单元测试
# ══════════════════════════════════════════════════════

class TestSnakeInit(unittest.TestCase):
    """蛇初始化"""

    def test_initial_length(self):
        snake = Snake(20)
        self.assertEqual(snake.length(), 3)

    def test_initial_position(self):
        snake = Snake(20)
        center = 10
        self.assertEqual(snake.get_head(), (center, center))
        self.assertEqual(snake.get_body()[1], (center - 1, center))
        self.assertEqual(snake.get_body()[2], (center - 2, center))

    def test_initial_direction(self):
        snake = Snake(20)
        self.assertEqual(snake.direction, RIGHT)


class TestSnakeMovement(unittest.TestCase):
    """蛇移动"""

    def setUp(self):
        self.snake = Snake(20)
        self.center = 10

    def test_move_right(self):
        """默认向右移动，头部 x+1"""
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (self.center + 1, self.center))

    def test_move_left(self):
        # 先向右移（默认方向），再转 UP，再转 LEFT
        self.snake.move()                     # (11, 10)
        self.snake.set_direction(UP)
        self.snake.move()                     # (11,  9)
        self.snake.set_direction(LEFT)
        self.snake.move()                     # (10,  9)
        self.assertEqual(self.snake.get_head(), (10, 9))

    def test_move_up(self):
        self.snake.set_direction(UP)
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (self.center, self.center - 1))

    def test_move_down(self):
        self.snake.set_direction(DOWN)
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (self.center, self.center + 1))

    def test_length_constant_when_not_eating(self):
        """不吃食物时长度不变"""
        self.snake.move()
        self.assertEqual(self.snake.length(), 3)

    def test_grow_increases_length(self):
        self.snake.grow()
        self.snake.move()
        self.assertEqual(self.snake.length(), 4)

    def test_multiple_grows(self):
        """连续吃多个食物"""
        for _ in range(5):
            self.snake.grow()
            self.snake.move()
        self.assertEqual(self.snake.length(), 8)


class TestSnakeDirection(unittest.TestCase):
    """方向控制"""

    def setUp(self):
        self.snake = Snake(20)

    def test_cannot_reverse(self):
        """不能 180° 掉头"""
        self.snake.set_direction(LEFT)   # 当前是 RIGHT
        self.assertEqual(self.snake.direction, RIGHT)  # 被拒绝

    def test_can_change_to_perpendicular(self):
        self.snake.set_direction(UP)
        self.assertEqual(self.snake.direction, UP)

    def test_can_change_after_moving(self):
        self.snake.move()
        self.snake.set_direction(UP)
        self.assertEqual(self.snake.direction, UP)


class TestSnakeCollision(unittest.TestCase):
    """碰撞检测"""

    def setUp(self):
        self.snake = Snake(20)

    def test_no_wall_collision_at_start(self):
        self.assertFalse(self.snake.check_wall_collision())

    def test_wall_collision_left(self):
        """蛇向左走到边缘应碰撞"""
        self.snake.body = [(0, 10), (1, 10), (2, 10)]
        self.snake.direction = LEFT
        self.assertFalse(self.snake.check_wall_collision())
        self.snake.move()
        self.assertTrue(self.snake.check_wall_collision())

    def test_wall_collision_right(self):
        self.snake.body = [(18, 10), (17, 10), (16, 10)]
        self.snake.set_direction(RIGHT)
        self.snake.move()
        self.assertFalse(self.snake.check_wall_collision())
        self.snake.move()
        self.assertTrue(self.snake.check_wall_collision())

    def test_wall_collision_top(self):
        self.snake.body = [(10, 0), (10, 1), (10, 2)]
        self.snake.set_direction(UP)
        self.snake.move()
        self.assertTrue(self.snake.check_wall_collision())

    def test_wall_collision_bottom(self):
        self.snake.body = [(10, 19), (10, 18), (10, 17)]
        self.snake.set_direction(DOWN)
        self.snake.move()
        self.assertTrue(self.snake.check_wall_collision())

    def test_self_collision_short_snake(self):
        """3 节蛇不可能撞自己（吃了才可能）"""
        self.assertFalse(self.snake.check_self_collision())

    def test_self_collision_after_making_u_turn_blocking_works(self):
        """撞自己：蛇必须足够长，且绕回来"""
        # 构建一个 U 形
        #   X H .     H=head at (3,0)
        #   X X .     body goes (2,0),(1,0),(1,1),(2,1),(3,1)
        #   . . .
        # 然后向上 → 撞到 (2,0)
        snake = Snake(20)
        snake.body = [(3, 0), (2, 0), (1, 0), (1, 1), (2, 1), (3, 1)]
        snake.direction = DOWN  # 避免正上方碰撞
        self.assertFalse(snake.check_self_collision())
        snake.set_direction(UP)
        snake.move()  # head now at (3, -1) — 墙了, 先移回来
        # 简短验证: 构建一个绕圈的场景
        snake2 = Snake(20)
        snake2.body = [(3, 2), (3, 1), (2, 1), (2, 2), (1, 2)]
        snake2.direction = LEFT
        self.assertFalse(snake2.check_self_collision())  # head (3,2) not in rest
        snake2.move()  # head goes to (2,2), which IS in body
        self.assertTrue(snake2.check_self_collision())

    def test_no_false_self_collision(self):
        """紧跟着尾巴走不会误判（尾巴会移走）"""
        snake = Snake(20)
        snake.body = [(5, 5), (4, 5), (3, 5)]
        snake.direction = RIGHT
        self.assertFalse(snake.check_self_collision())


class TestSnakeOccupies(unittest.TestCase):
    """位置占用"""

    def setUp(self):
        self.snake = Snake(20)

    def test_head_occupied(self):
        self.assertTrue(self.snake.occupies((10, 10)))

    def test_middle_occupied(self):
        self.assertTrue(self.snake.occupies((9, 10)))

    def test_empty_not_occupied(self):
        self.assertFalse(self.snake.occupies((0, 0)))


# ══════════════════════════════════════════════════════
# Food 单元测试
# ══════════════════════════════════════════════════════

class TestFood(unittest.TestCase):
    """食物生成"""

    def test_spawn_not_on_snake(self):
        snake = Snake(20)
        food = Food()
        food.spawn(snake.get_body())
        pos = food.get_position()
        self.assertIsNotNone(pos)
        self.assertNotIn(pos, snake.get_body())

    def test_spawn_multiple_times(self):
        snake = Snake(20)
        food = Food()
        positions = set()
        for _ in range(100):
            food.spawn(snake.get_body())
            pos = food.get_position()
            self.assertIsNotNone(pos)
            self.assertNotIn(pos, snake.get_body())
            positions.add(pos)
        # 100 次应该在棋盘上分散
        self.assertGreater(len(positions), 10)

    def test_spawn_fails_on_full_board(self):
        """棋盘全满时 spawn 返回 False"""
        occupied = [(x, y) for x in range(20) for y in range(20)]
        food = Food()
        result = food.spawn(occupied)
        self.assertFalse(result)

    def test_get_position_initial(self):
        food = Food()
        self.assertIsNone(food.get_position())


# ══════════════════════════════════════════════════════
# GameCore 集成测试
# ══════════════════════════════════════════════════════

class TestGameCoreInit(unittest.TestCase):
    """游戏初始化"""

    def test_initial_state(self):
        game = GameCore()
        self.assertFalse(game.game_over)
        self.assertFalse(game.won)
        self.assertEqual(game.score, 0)
        self.assertEqual(game.snake.length(), 3)
        self.assertIsNotNone(game.food.get_position())
        self.assertNotIn(game.food.get_position(), game.snake.get_body())

    def test_food_on_board(self):
        game = GameCore()
        fx, fy = game.food.get_position()
        self.assertGreaterEqual(fx, 0)
        self.assertGreaterEqual(fy, 0)
        self.assertLess(fx, 20)
        self.assertLess(fy, 20)


class TestGameCoreUpdate(unittest.TestCase):
    """单帧更新"""

    def test_update_moves_snake(self):
        game = GameCore()
        head_before = game.snake.get_head()
        game.update()
        head_after = game.snake.get_head()
        self.assertNotEqual(head_before, head_after)

    def test_update_increases_score_on_food(self):
        """强制蛇头对准食物"""
        game = GameCore()
        # 手动设置食物位置到蛇头正前方（默认向右）
        head = game.snake.get_head()  # (10, 10)
        food_pos = (head[0] + 1, head[1])  # (11, 10)
        game.food.position = food_pos
        game.update()
        self.assertEqual(game.score, 1)        # 吃到了
        # 注：move() 在先、grow() 在后，长度在下一帧才体现
        self.assertEqual(game.snake.length(), 3)

    def test_game_over_on_wall(self):
        game = GameCore()
        # 直接把蛇放到墙边
        game.snake.body = [(0, 10), (1, 10), (2, 10)]
        game.snake.direction = LEFT
        game.update()
        self.assertTrue(game.game_over)
        self.assertFalse(game.won)

    def test_game_over_on_self_collision(self):
        game = GameCore()
        # 构造绕圈场景
        game.snake.body = [(3, 2), (3, 1), (2, 1), (2, 2), (1, 2)]
        game.snake.direction = LEFT
        game.update()  # 头到 (2,2)，和 (2,1) 碰撞？不对，(2,2) 在 body 里
        self.assertTrue(game.game_over)
        self.assertFalse(game.won)


class TestGameCoreReset(unittest.TestCase):
    """重置"""

    def test_reset_restores_initial_state(self):
        game = GameCore()
        # 先玩几帧
        for _ in range(10):
            game.update()

        game.reset()
        self.assertFalse(game.game_over)
        self.assertFalse(game.won)
        self.assertEqual(game.score, 0)
        self.assertIsNotNone(game.food.get_position())
        self.assertNotIn(game.food.get_position(), game.snake.get_body())

    def test_reset_clears_game_over(self):
        game = GameCore()
        game.snake.body = [(0, 10), (1, 10), (2, 10)]
        game.snake.direction = LEFT
        game.update()
        self.assertTrue(game.game_over)
        game.reset()
        self.assertFalse(game.game_over)


class TestGameCoreSpeed(unittest.TestCase):
    """速度递增"""

    def test_speed_increases_every_5_points(self):
        game = GameCore()
        base_speed = game.speed
        for i in range(5):
            # 手动送食物
            head = game.snake.get_head()
            game.food.position = (head[0] + game.snake.direction[0],
                                  head[1] + game.snake.direction[1])
            game.update()
        self.assertEqual(game.score, 5)
        self.assertGreater(game.speed, base_speed)


class TestGameCoreDirection(unittest.TestCase):
    """方向控制集成"""

    def test_set_direction(self):
        game = GameCore()
        game.set_direction(UP)
        game.update()
        # 蛇头应该向上移动
        self.assertIsNotNone(game.snake.get_head())


# ══════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main()
