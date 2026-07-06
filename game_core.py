"""
game_core.py — 贪吃蛇核心逻辑
完全独立于 UI 层，可纯单元测试。
"""

import random

# 方向常量
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

ALL_DIRECTIONS = (UP, DOWN, LEFT, RIGHT)


class Snake:
    """蛇身管理"""

    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        center = grid_size // 2
        # 初始 3 节，向左
        self.body = [(center, center), (center - 1, center), (center - 2, center)]
        self.direction = RIGHT
        self._grow_flag = False

    # ── 驱动 ──────────────────────────────────────────

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self._grow_flag:
            self.body.pop()
        else:
            self._grow_flag = False

    def grow(self):
        self._grow_flag = True

    # ── 碰撞 ──────────────────────────────────────────

    def check_self_collision(self) -> bool:
        return self.body[0] in self.body[1:]

    def check_wall_collision(self) -> bool:
        x, y = self.body[0]
        return not (0 <= x < self.grid_size and 0 <= y < self.grid_size)

    # ── 方向 ──────────────────────────────────────────

    def set_direction(self, new_dir):
        """不准 180° 掉头"""
        if (new_dir[0] != -self.direction[0]) or (new_dir[1] != -self.direction[1]):
            self.direction = new_dir

    # ── 查询 ──────────────────────────────────────────

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body

    def occupies(self, pos) -> bool:
        return pos in self.body

    def length(self) -> int:
        return len(self.body)


class Food:
    """食物位置管理"""

    def __init__(self):
        self.position = None

    def spawn(self, occupied: list) -> bool:
        """在未被占据的位置随机生成食物。棋盘满则返回 False。"""
        available = [
            (x, y)
            for x in range(20)
            for y in range(20)
            if (x, y) not in occupied
        ]
        if not available:
            return False
        self.position = random.choice(available)
        return True

    def get_position(self):
        return self.position


class GameCore:
    """
    游戏核心状态机 —— 纯逻辑，不依赖任何 UI 库。
    每帧调用 update() 即可推进。
    """

    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        self.snake = Snake(grid_size)
        self.food = Food()
        self.food.spawn(self.snake.get_body())

        self.score = 0
        self.game_over = False
        self.won = False
        self.speed = 10  # 初始更新频率 (FPS)

    # ── 主循环 ────────────────────────────────────────

    def update(self):
        if self.game_over:
            return

        self.snake.move()

        # 碰撞检测
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.game_over = True
            self.won = False
            return

        # 吃到食物
        if self.snake.get_head() == self.food.get_position():
            self.snake.grow()
            self.score += 1

            # 每 5 分提速
            if self.score % 5 == 0 and self.speed < 25:
                self.speed += 1

            # 全满 → 胜利
            if len(self.snake.get_body()) >= self.grid_size * self.grid_size:
                self.game_over = True
                self.won = True
                return

            if not self.food.spawn(self.snake.get_body()):
                self.game_over = True
                self.won = True

    # ── 操作 ──────────────────────────────────────────

    def set_direction(self, direction):
        self.snake.set_direction(direction)

    def reset(self):
        self.__init__(self.grid_size)
