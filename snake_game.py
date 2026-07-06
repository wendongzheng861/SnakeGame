#!/usr/bin/env python3
"""
snake_game.py — 贪吃蛇 (Curses 终端版)
启动：python3 snake_game.py
"""

import curses
import time
from game_core import GameCore, UP, DOWN, LEFT, RIGHT

# ── 颜色定义 ─────────────────────────────────────────

SNAKE_HEAD  = 1   # 绿色
SNAKE_BODY  = 2   # 草绿
SNAKE_TAIL  = 3   # 墨绿
FOOD_COLOR  = 4   # 红色
TEXT_COLOR  = 5   # 白色
GAME_OVER_C = 6   # 红底白字
BG_DARK     = 7   # 深灰背景
BORDER_C    = 8   # 边框色
GRID_C      = 9   # 网格色
BG_CELL     = 10  # 空网格背景


def init_colors():
    curses.start_color()
    curses.use_default_colors()  # 终端默认背景

    # 前景色固定，背景可自定义
    # pair_number = (前景, 背景)
    curses.init_pair(SNAKE_HEAD,  curses.COLOR_GREEN,   -1)
    curses.init_pair(SNAKE_BODY,  curses.COLOR_YELLOW,  -1)
    curses.init_pair(SNAKE_TAIL,  curses.COLOR_CYAN,    -1)
    curses.init_pair(FOOD_COLOR,  curses.COLOR_RED,     -1)
    curses.init_pair(TEXT_COLOR,  curses.COLOR_WHITE,   -1)
    curses.init_pair(GAME_OVER_C, curses.COLOR_WHITE,   curses.COLOR_RED)
    curses.init_pair(BG_DARK,     curses.COLOR_BLACK,   -1)
    curses.init_pair(BORDER_C,    curses.COLOR_WHITE,   -1)
    curses.init_pair(GRID_C,      curses.COLOR_BLACK,   curses.COLOR_BLACK)
    curses.init_pair(BG_CELL,     curses.COLOR_WHITE,   curses.COLOR_BLACK)


# ── 绘图函数 ─────────────────────────────────────────

def draw_grid(stdscr, game):
    """画 20×20 棋盘"""
    offset_x = 2
    offset_y = 2

    for y in range(game.grid_size):
        for x in range(game.grid_size):
            ch = ' '
            pair = BG_CELL

            # 蛇身
            body = game.snake.get_body()
            if (x, y) == game.snake.get_head():
                # 蛇头 — 根据方向显示箭头
                d = game.snake.direction
                if d == RIGHT:
                    ch = '▶'
                elif d == LEFT:
                    ch = '◀'
                elif d == UP:
                    ch = '▲'
                else:
                    ch = '▼'
                pair = SNAKE_HEAD
            elif (x, y) in body:
                ch = '■'
                # 越靠尾颜色越深
                idx = body.index((x, y))
                if idx > len(body) * 0.7:
                    pair = SNAKE_TAIL
                else:
                    pair = SNAKE_BODY
            elif game.food.get_position() and (x, y) == game.food.get_position():
                ch = '●'
                pair = FOOD_COLOR
            else:
                # 空网格 — 交替深浅方便看
                if (x + y) % 2 == 0:
                    ch = '·'
                    pair = BG_CELL
                else:
                    ch = ' '
                    pair = BG_CELL

            try:
                stdscr.addstr(offset_y + y, offset_x + x * 2, ch, curses.color_pair(pair))
            except curses.error:
                pass


def draw_border(stdscr, game):
    """画棋盘边框"""
    offset_x = 2
    offset_y = 2
    w = game.grid_size * 2
    h = game.grid_size

    # 四角
    try:
        stdscr.addch(offset_y - 1, offset_x - 2,     '┌', curses.color_pair(BORDER_C))
        stdscr.addch(offset_y - 1, offset_x - 1 + w, '┐', curses.color_pair(BORDER_C))
        stdscr.addch(offset_y + h, offset_x - 2,     '└', curses.color_pair(BORDER_C))
        stdscr.addch(offset_y + h, offset_x - 1 + w, '┘', curses.color_pair(BORDER_C))

        # 横线
        stdscr.addstr(offset_y - 1, offset_x - 1, '─' * (w - 1), curses.color_pair(BORDER_C))
        stdscr.hline(offset_y + h, offset_x - 1, '─', w - 1, curses.color_pair(BORDER_C))

        # 竖线（分别画避免 utf-8 宽度问题）
        for row in range(h):
            stdscr.addch(offset_y + row, offset_x - 2, '│', curses.color_pair(BORDER_C))
            stdscr.addch(offset_y + row, offset_x - 1 + w, '│', curses.color_pair(BORDER_C))
    except curses.error:
        pass


def draw_hud(stdscr, game):
    """画顶部信息栏"""
    try:
        stdscr.addstr(0, 2, f"🐍 Snake Game", curses.color_pair(TEXT_COLOR) | curses.A_BOLD)
        stdscr.addstr(1, 2, f"Score: {game.score}  |  Length: {game.snake.length()}  |  Level: {game.speed - 9}",
                      curses.color_pair(TEXT_COLOR))
    except curses.error:
        pass


def draw_game_over(stdscr, game):
    """游戏结束 / 胜利 画面"""
    h, w = stdscr.getmaxyx()
    if game.won:
        msg = "🎉 YOU WIN! 🎉"
    else:
        msg = "💀 GAME OVER 💀"

    center_x = w // 2
    center_y = h // 2

    # 半透明蒙版效果 — 直接填充空白
    try:
        for y in range(center_y - 4, center_y + 5):
            stdscr.addstr(y, center_x - 15, " " * 30, curses.color_pair(GAME_OVER_C) | curses.A_BOLD)
    except curses.error:
        pass

    try:
        stdscr.addstr(center_y - 2, center_x - len(msg) // 2, msg,
                      curses.color_pair(GAME_OVER_C) | curses.A_BOLD)
        stdscr.addstr(center_y,     center_x - 12, f"Score: {game.score}",
                      curses.color_pair(TEXT_COLOR) | curses.A_BOLD)
        stdscr.addstr(center_y + 2, center_x - 20,
                      "Press SPACE or ENTER to restart",
                      curses.color_pair(TEXT_COLOR))
        stdscr.addstr(center_y + 3, center_x - 16,
                      "Press ESC or Q to quit",
                      curses.color_pair(TEXT_COLOR))
    except curses.error:
        pass


def draw_pause(stdscr):
    """暂停画面"""
    h, w = stdscr.getmaxyx()
    msg = "⏸ PAUSED"
    sub = "Press SPACE to continue"
    try:
        stdscr.addstr(h // 2 - 1, w // 2 - len(msg) // 2, msg,
                      curses.color_pair(TEXT_COLOR) | curses.A_BOLD)
        stdscr.addstr(h // 2 + 1, w // 2 - len(sub) // 2, sub,
                      curses.color_pair(TEXT_COLOR))
    except curses.error:
        pass


# ── 主函数 ──────────────────────────────────────────

def main(stdscr):
    init_colors()
    curses.curs_set(0)        # 隐藏光标
    stdscr.nodelay(True)      # 非阻塞输入
    stdscr.timeout(100)       # getch 超时 ms

    game = GameCore()
    paused = False
    game_over_state = False

    while True:
        # ── 输入 ──
        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):   # esc / q
            break

        # 游戏结束后处理
        if game.game_over:
            if key in (ord(' '), ord('\n'), ord('\r'), ord('r'), ord('R')):
                game.reset()
                paused = False
                game_over_state = False
            continue

        if key == ord(' '):
            paused = not paused
            continue

        if not paused:
            if key in (curses.KEY_UP, ord('w'), ord('W')):
                game.set_direction(UP)
            elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
                game.set_direction(DOWN)
            elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
                game.set_direction(LEFT)
            elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                game.set_direction(RIGHT)

        # ── 更新 ──
        if not paused and not game.game_over:
            game.update()

        # ── 重绘 ──
        stdscr.erase()
        draw_hud(stdscr, game)
        draw_border(stdscr, game)
        draw_grid(stdscr, game)

        # 操作提示
        try:
            hint = "Arrow/WASD: Move  |  SPACE: Pause  |  Q/ESC: Quit"
            stdscr.addstr(2 + game.grid_size + 1, 2, hint, curses.color_pair(BORDER_C))
        except curses.error:
            pass

        if game.game_over:
            draw_game_over(stdscr, game)
        elif paused:
            draw_pause(stdscr)

        stdscr.refresh()

        # 用游戏速度控制帧率
        time.sleep(1.0 / game.speed)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
