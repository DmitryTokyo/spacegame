import asyncio
import time
import curses
import random
from itertools import cycle

from curses_tools import draw_frame, read_controls, get_frame_size
from animation_frame import get_rocket_frames, get_garbage_frames
from pysics import update_speed
from obstacles import Obstacle, show_obstacles
from explosion import explode


TIC_TIMEOUT = 0.1
SCREEN_WIDE, SCREEN_HEIGHT = 0, 0
COROUTINES = []
OBSTACLES = []
STAR = '*+:.'
OBSTACLES_IN_LAST_COLLISION = []


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        loop = random.randint(1, 21)
        await sleep(loop)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def control_spaceship(canvas, rocket_frames, row, column):
    rocket_height, rocket_wide = get_frame_size(rocket_frames[0])
    rocket_frames = cycle(rocket_frames)
    row_speed = column_speed = 0 

    while True:
        rocket_frame = next(rocket_frames) 
        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)
        if space_pressed:
            COROUTINES.append(fire(canvas, row - 1, column + rocket_wide // 2))
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        row += row_speed
        column += column_speed

        if column <= 1 or column >= SCREEN_WIDE - rocket_wide:
            column -= column_speed
        if row <= 1 or row >= SCREEN_HEIGHT - rocket_height:
            row -= row_speed
        draw_rocket(canvas, rocket_frame, row, column)
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-1.3, columns_speed=0):
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
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_LAST_COLLISION.append(obstacle)
                return
            
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fill_orbit_with_garbage(canvas, garbage_frames):
    while True:
        COROUTINES.append(fly_garbage(canvas, random.randint(1, SCREEN_WIDE-1), random.choice(garbage_frames)))
        await sleep(15)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    obstacle_row, obstacle_column = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, obstacle_row, obstacle_column)
    OBSTACLES.append(obstacle)
    COROUTINES.append(show_obstacles(canvas, OBSTACLES))

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed
        if obstacle in OBSTACLES_IN_LAST_COLLISION:
            OBSTACLES.remove(obstacle)
            OBSTACLES_IN_LAST_COLLISION.remove(obstacle)
            COROUTINES.append(explode(canvas, row + obstacle_row//2, column + obstacle_column//2))
            return
    else:        
        OBSTACLES.remove(obstacle)
        

async def sleep(tic=1):
    for _ in range(tic): 
        await asyncio.sleep(0)


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
    COROUTINES.extend([
        fill_orbit_with_garbage(canvas, garbage_frames),
        control_spaceship(canvas, rocket_frames, SCREEN_HEIGHT//2, SCREEN_WIDE//2)
    ])

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
