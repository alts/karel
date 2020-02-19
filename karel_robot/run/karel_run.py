#!/usr/bin/env python3
"""  Karel implementation in Python (with curses).
+--------------------------------------------------------------------
| As a standalone app, this script opens a text file map and lets   |
| the user control the robot using a keyboard.                      |
|                                                                   |
| Write your Karel program in Python by importing `karel_robot.run` |
| and using the simple functions like `move()` and `turn_left()`.   |
| See the README on github.com/xsebek/karel for more details.       |
| Note that the curses screen starts up upon import.                |
+-------------------------------------------------------------------+
"""
import argparse
from curses import endwin
from errno import ENOENT, EINVAL

from .. import *

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    dest='karelmap',
    help="a text file with a map of karel world",
    metavar="YOUR_WORLD.karelmap")
args = parser.parse_args()

###########################################################
#                     KAREL START-UP                      #
###########################################################


# Board is loaded and starts the curses window
try:
    karel, karel_map = parse_map(args.karelmap)
    w = Window(karel, karel_map)
except IOError as e:
    print("Could not open karel map file:\n" + str(e))
    exit(ENOENT)
except RuntimeError as e:
    print("Failed parsing map:\n" + str(e))
    exit(EINVAL)
except RobotError as e:
    endwin()
    print("There was a problem with curses:\n" + str(e))
    exit(EINVAL)


def refresh(function, moved=False):
    """Execute a Board method and redraw. """
    try:
        result = function()
        w.redraw(moved)
        return result
    except RobotError as _rob_e:
        w.draw_exception(_rob_e)


###########################################################
#                     KAREL FUNCTIONS                     #
###########################################################

# Movement
def move():
    """Karel tries to move in the direction he is facing. """
    refresh(w.move, True)

def turn_left():
    """Karel turns left. """
    refresh(w.karel.turn_left)

def turn_right():
    """Karel turns right. """
    refresh(w.karel.turn_right)

# Beepers
def pick_beeper():
    """Karel tries to pick up a beeper. """
    refresh(w.pick_beeper)

def put_beeper():
    """Karel puts down a beeper (if he has any). """
    refresh(w.put_beeper)

def beeper_is_present():
    """True iff Karel stands on a beeper. """
    return w.beeper_is_present()

# Walls
def front_is_blocked():
    """True iff Karel can't move forward. """
    return w.front_is_blocked()

def front_is_treasure():
    """True iff Karel stands in front of a Treasure. """
    return w.front_is_treasure()

# Direction
def facing_north():
    """True iff Karel is facing north (^). """
    return w.karel.facing_north()

def facing_south():
    """True iff Karel is facing south (v). """
    return w.karel.facing_south()

def facing_east():
    """True iff Karel is facing east (>). """
    return w.karel.facing_east()

def facing_west():
    """True iff Karel is facing west (<). """
    return w.karel.facing_west()

# Execution
def set_speed(spd):
    """Set how fast Karel moves (0 to 100). """
    w.speed = w.valid_speed(spd)

def set_karel_beepers(b=0):
    """Set Karel's beepers, with None working as inf. """
    w.karel.beepers = b if b is None else max(0, round(b))

def pause():
    """Pause execution, press any key to continue. """
    w.pause()


###########################################################
#             INTERACTIVE CLIENT FOR TESTING              #
###########################################################

def interactive():
    """Command the created Board using your keyboard. """
    set_speed(100)  # do not wait
    curses.noecho()
    curses.cbreak()
    w.screen.keypad(1)
    while True:
        # end if user presses 'c'
        ch = w.screen.getch()
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
                w.draw_exception("Use arrows to move, pIck, pUt and Quit.")
        time.sleep(0.1)


if __name__ == '__main__':
    interactive()
