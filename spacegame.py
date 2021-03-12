import asyncio
import time
import curses
import random
from itertools import cycle

from curses_tools import draw_frame, read_controls, get_frame_size
from animation_frame import get_rocket_frames, get_garbage_frames

TIC_TIMEOUT = 0.1
SCREEN_WIDE, SCREEN_HEIGHT = 0, 0
COROUTINES = []
STAR = '*+:.'


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


async def control_spaceship(canvas, rocket_frames, row, column):
    rocket_height, rocket_wide = get_frame_size(rocket_frames[0])
    rocket_frames = cycle(rocket_frames)

    while True:
        rocket_frame = next(rocket_frames)
        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)
        row += rows_direction
        column += columns_direction
        if column <= 1 or column >= SCREEN_WIDE - rocket_wide:
            column -= columns_direction
        if row <= 1 or row >= SCREEN_HEIGHT - rocket_height:
            row -= rows_direction
        draw_rocket(canvas, rocket_frame, row, column)
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
        COROUTINES.append(fly_garbage(canvas, random.randint(1, SCREEN_WIDE-1), random.choice(garbage_frames)))
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
    rocket_frames = get_rocket_frames()
    garbage_frames = get_garbage_frames()

    for column in range(100):
        star_row = random.randint(1, SCREEN_HEIGHT-1)
        star_column = random.randint(1, SCREEN_WIDE-1)
        star_type = random.choice(STAR)
        COROUTINES.append(blink(canvas, star_row, star_column, star_type))
    COROUTINES.append(fire(canvas, SCREEN_HEIGHT/2, SCREEN_WIDE/2))
    COROUTINES.append(fill_orbit_with_garbage(canvas, garbage_frames))
    COROUTINES.append(control_spaceship(canvas, rocket_frames, SCREEN_HEIGHT/2, SCREEN_WIDE/2))

    canvas.nodelay(True)
    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
            if len(COROUTINES) == 0:
                break

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    screen = curses.initscr()
    curses.curs_set(False)
    curses.update_lines_cols()
    SCREEN_HEIGHT, SCREEN_WIDE = screen.getmaxyx()
    curses.wrapper(draw)