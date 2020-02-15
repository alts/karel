#!/usr/bin/env python3
"""Karel implementation in Python (with curses).

Import this file to command Karel using simple functions.
The curses screen starts upon import.

Note that all locally defined values are prefixed with '_'
to deter anyone who may be tempted to misuse them.
"""
from curses import endwin
import sys
import errno
from karel import *

def karel_help():
    print("Karel expected usage:")
    print("python3 YOUR_PROGRAM.py YOUR_WORLD.karelmap")
    print("\nFor interactive mode:")
    print("python3 karel_run.py YOUR_WORLD.karelmap")

###########################################################
#                     KAREL START-UP                      #
###########################################################


# Board is loaded and starts the curses window
try:
    if len(sys.argv) == 1:
        karel_help()
        exit(errno.EPERM)
    _karel, _karel_map = construct_map(sys.argv[1])
    _w = Window(_karel, _karel_map)
except IOError as _e:
    print("Could not open karel map file:\n" + str(_e))
    exit(errno.ENOENT)
except RuntimeError as _e:
    print("Failed parsing map:\n" + str(_e))
    exit(errno.EINVAL)
except RobotError as _e:
    endwin()
    print("There was a problem with curses:\n" + str(_e))
    exit(errno.EINVAL)


def refresh(func, moved=False):
    """Execute a Board method and redraw. """
    try:
        res = func()
        _w.redraw(moved)
        return res
    except RobotError as _rob_e:
        _w.draw_exception(_rob_e)


###########################################################
#                     KAREL FUNCTIONS                     #
###########################################################

# Movement
def move():
    """Karel tries to move in the direction he is facing. """
    refresh(_w.move, True)

def turn_left():
    """Karel turns left. """
    refresh(_w.karel.turn_left)

def turn_right():
    """Karel turns right. """
    refresh(_w.karel.turn_right)

# Beepers
def pick_beeper():
    """Karel tries to pick up a beeper. """
    refresh(_w.pick_beeper)

def put_beeper():
    """Karel puts down a beeper (if he has any). """
    refresh(_w.put_beeper)

def beeper_is_present():
    """True iff Karel stands on a beeper. """
    return _w.beeper_is_present()

# Walls
def front_is_blocked():
    """True iff Karel can't move forward. """
    return _w.front_is_blocked()

def front_is_treasure():
    """True iff Karel stands in front of a Treasure. """
    return _w.front_is_treasure()

# Direction
def facing_north():
    """True iff Karel is facing north (^). """
    return _w.karel.facing_north()

def facing_south():
    """True iff Karel is facing south (v). """
    return _w.karel.facing_south()

def facing_east():
    """True iff Karel is facing east (>). """
    return _w.karel.facing_east()

def facing_west():
    """True iff Karel is facing west (<). """
    return _w.karel.facing_west()

# Execution
def set_speed(spd):
    """Set how fast Karel moves (0 to 100). """
    _w.speed = _w.valid_speed(spd)

def set_karel_beepers(b=0):
    """Set Karel's beepers, with None working as inf. """
    _w.karel.beepers = b if b is None else max(0, round(b))

def pause():
    """Pause execution, press any key to continue. """
    _w.pause()


###########################################################
#             INTERACTIVE CLIENT FOR TESTING              #
###########################################################

def interactive():
    """Command the created Board using your keyboard. """
    set_speed(100)  # do not wait
    curses.noecho()
    curses.cbreak()
    _w.screen.keypad(1)
    while True:
        # end if user presses 'c'
        ch = _w.screen.getch()
        if ch != curses.ERR:
            if ch == ord('q'):
                exit()
            elif ch == curses.KEY_LEFT:
                turn_left()
            elif ch == curses.KEY_RIGHT:
                turn_right()
            elif ch == curses.KEY_UP:
                move()
            elif ch == ord('u'):
                put_beeper()
            elif ch == ord('i'):
                pick_beeper()
            else:
                _w.draw_exception("Use arrows to move, pIck, pUt and Quit.")
        time.sleep(0.1)


if __name__ == '__main__':
    interactive()
