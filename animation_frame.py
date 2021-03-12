from curses_tools import get_frame_size


def get_rocket_frames():
    rocket_frame_files = ['animation/rocket_frame_1.txt',
                          'animation/rocket_frame_2.txt']
    
    rocket_frames = []
    for rocket_frame_file in rocket_frame_files:
        with open(rocket_frame_file, 'r') as file:
            rocket_frames.append(file.read())

    rocket_height, rocket_wide = get_frame_size(rocket_frames[0])

    return rocket_frames


def get_garbage_frames():
    garbage_frame_files = [
        'animation/duck.txt',
        'animation/hubble.txt',
        'animation/lamp.txt',
        'animation/trash_large.txt',
        'animation/trash_small.txt',
        'animation/trash_xl.txt'
    ]

    garbage_frames = []
    for garbage_frame_file in garbage_frame_files:
        with open(garbage_frame_file, 'r') as file:
            garbage_frames.append(file.read())
    
    return garbage_frames