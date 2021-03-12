import asyncio
import time
import curses
import random
from itertools import cycle

from curses_tools import draw_frame, read_controls, get_frame_size
from animation_frame import get_rocket_frames_and_size, get_garbage_frames
from fire import fire

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        loop = random.randint(1, 21)
        for _ in range(loop):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fill_orbit_with_garbage(canvas, garbage_frames):
    while True:
        coroutines.append(fly_garbage(canvas, random.randint(1, max_border_wide-1), random.choice(garbage_frames)))
        for _ in range(15):
            await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


def draw_rocket(canvas, rocket_frame, row, column):
    draw_frame(canvas, row, column, rocket_frame)
    canvas.refresh()
    draw_frame(canvas, row, column, rocket_frame, negative=True)


def draw(canvas):
    global coroutines
    global max_border_wide
    rocket_frames, rocket_height, rocket_wide = get_rocket_frames_and_size()
    garbage_frames = get_garbage_frames()

    max_border_height, max_border_wide = canvas.getmaxyx()
    rocket_position_row = max_border_height/2
    rocket_position_column = max_border_wide/2

    # Создание списка корутин
    star = '*+:.'
    coroutines = []
    for column in range(100):
        star_row = random.randint(1, max_border_height-1)
        star_column = random.randint(1, max_border_wide-1)
        star_type = random.choice(star)
        coroutines.append(blink(canvas, star_row, star_column, star_type))
    coroutines.append(fire(canvas, rocket_position_row, rocket_position_column))
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_frames))

    canvas.nodelay(True)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
            if len(coroutines) == 0:
                break

        # Определение местоположения ракеты, считывание кнопок, отрисовка ракеты
        rocket_frame = next(rocket_frames)
        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)
        rocket_position_row += rows_direction
        rocket_position_column += columns_direction
        if rocket_position_column <= 1 or rocket_position_column >= max_border_wide - rocket_wide:
            rocket_position_column -= columns_direction
        if rocket_position_row <= 1 or rocket_position_row >= max_border_height - rocket_height:
            rocket_position_row -= rows_direction
        draw_rocket(canvas, rocket_frame, rocket_position_row, rocket_position_column)

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.initscr()
    curses.curs_set(False)
    curses.update_lines_cols()
    curses.wrapper(draw)
