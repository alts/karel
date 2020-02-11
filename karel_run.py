#!/usr/bin/env python3
import sys
from karel import *

###########################################################
#                     KAREL START-UP                      #
###########################################################

# Board is loaded and starts the curses window
try:
    if len(sys.argv) > 1:
        _b = Board(sys.argv[1])
    else:
        karel_help()
        exit(1)
except IOError as e:
    print("Could not open karel map file:\n" + str(e))
    exit(2)
except RuntimeError as r:
    print("Failed parsing map:\n" + str(r))
    exit(3)


def refresh(func, moved=False):
    """Execute a Board method and redraw. """
    try:
        res = func()
        _b.redraw(moved)
        return res
    except RobotError as w:
        _b.draw_exception(w)


###########################################################
#                     KAREL FUNCTIONS                     #
###########################################################

# Movement
def move():
    """Karel moves in the direction he is facing. """
    refresh(_b.move, True)

def turn_left():
    """Karel turns left. """
    refresh(_b.karel.turn_left)

def turn_right():
    """Karel turns right. """
    refresh(_b.karel.turn_right)

# Beepers
def pick_beeper():
    """Karel tries to pick up a beeper. """
    refresh(_b.pick_beeper)

def put_beeper():
    """Karel puts down a beeper (if he has any). """
    refresh(_b.put_beeper)

def beeper_is_present():
    """True iff Karel stands on a beeper. """
    return _b.beeper_is_present()

# Walls
def front_is_blocked():
    """True iff Karel can't move forward. """
    return _b.front_is_blocked()

def front_is_treasure():
    """True if Karel is standing in front of a Treasure. """
    return _b.front_is_treasure()

# Direction
def facing_north():
    """True iff Karel is facing north (^). """
    return _b.karel.facing_north()

def facing_south():
    """True iff Karel is facing south (v). """
    return _b.karel.facing_south()

def facing_east():
    """True iff Karel is facing east (>). """
    return _b.karel.facing_east()

def facing_west():
    """True iff Karel is facing west (<). """
    return _b.karel.facing_west()

# Execution
def set_speed(spd):
    """Set how fast Karel moves (0 to 100). """
    _b.speed = _b.valid_speed(spd)

def set_karel_beepers(b=0):
    """Set Karel's beepers, 0+ and None means inf. """
    _b.karel.beepers = b if b is None else max(0, round(b))

def stop():
    """End execution. """
    _b.complete()

def pause():
    """Pause execution, press any key to continue. """
    _b.pause()


###########################################################
#             INTERACTIVE CLIENT FOR TESTING              #
###########################################################

def interactive():
    """Command the created Board using your keyboard. """
    set_speed(100)  # do not wait
    curses.noecho()
    curses.cbreak()
    _b.screen.keypad(1)
    _b.screen.nodelay(True)
    while True:
        # end if user presses 'c'
        ch = _b.screen.getch()
        if ch != curses.ERR:
            if ch == ord('q'):
                stop()
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
                _b.draw_exception("Use arrows to move, pIck, pUt and Quit.")
        time.sleep(0.1)


if __name__ == '__main__':
    interactive()
