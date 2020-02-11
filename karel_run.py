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
    print("Could not open karel map file.", file=sys.stderr)
    exit(2)
except RuntimeError as r:
    print("Failed parsing map:\n", file=sys.stderr)
    print(r, file=sys.stderr)
    exit(3)


def refresh(func, moved=False):
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
def move(): refresh(_b.move, True)
def turn_left(): refresh(_b.karel.turn_left)
def turn_right(): refresh(_b.karel.turn_right)
def stop(): _b.complete()
def pause(): _b.pause()
# Beepers
def pick_beeper(): refresh(_b.pick_beeper)
def put_beeper(): refresh(_b.put_beeper)
def beeper_is_present(): return _b.beeper_is_present()
# Walls
def front_is_blocked(): return _b.front_is_blocked()
def front_is_treasure(): return _b.front_is_treasure()
# Direction
def facing_north(): return _b.karel.facing_north()
def facing_south(): return _b.karel.facing_south()
def facing_east(): return _b.karel.facing_east()
def facing_west(): return _b.karel.facing_west()
# Settings
def set_speed(spd): _b.speed = _b.valid_speed(spd)
def set_karel_beepers(b=0): _b.karel.beepers = b if b is None \
                                                 else max(0, round(b))


###########################################################
#             INTERACTIVE CLIENT FOR TESTING              #
###########################################################

def interactive():
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
