# 🐍 Snake Game — 经典贪吃蛇

一个用 Python **curses** 编写的经典贪吃蛇游戏，零外部依赖。

## 快速开始

```bash
python3 snake_game.py
```

## 操作

| 按键 | 功能 |
|------|------|
| ↑ ↓ ← → / WASD | 控制方向 |
| Space | 暂停 / 继续 |
| Q / ESC | 退出 |
| Space / Enter | 重新开始（结束画面） |

## 游戏特性

- 🎮 经典贪吃蛇玩法，20×20 棋盘
- 📈 每吃 5 个食物加速，最高 25 级
- 🏆 蛇填满棋盘时触发胜利
- 📊 实时显示分数、长度、等级
- 🎨 彩色蛇身渐变、蛇头方向指示
- 📝 完整单元测试覆盖

## 项目结构

```
SnakeGame/
├── snake_game.py     # 主程序（curses UI）
├── game_core.py      # 核心逻辑（纯 Python，可测试）
├── test_snake.py     # 单元测试（unittest）
└── README.md         # 说明文档
```

## 测试

```bash
python3 -m pytest test_snake.py -v
# 或
python3 test_snake.py
```

## 技术亮点

- **逻辑与 UI 分离**：`game_core.py` 零依赖，可单独测试
- **全覆盖测试**：蛇移动、碰撞、食物生成、游戏状态机、重置
- **零外部依赖**：只用了 Python 标准库
