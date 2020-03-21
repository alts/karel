#!/usr/bin/env python3
""" Karel implementation in Python (with curses).

As a standalone app, this script opens a text file map and lets
the user control the robot using a keyboard.

Write your Karel program in Python by importing karel_robot.run
and using the simple functions like move() and turn_left().
See the README on github.com/xsebek/karel for more details.

Note that the curses screen starts up upon import.

LICENSE

The karel_robot package is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

The karel_robot package is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the karel_robot package.
If not, see `<https://www.gnu.org/licenses/>`_.
"""
from curses import endwin, KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_HELP, KEY_RESIZE
from errno import ENOENT, EINVAL
from sys import stderr

from .. import *
from ..parsers import *


###########################################################
#                     KAREL START-UP                      #
###########################################################

parser = get_parser()

# ignore_robot_errors: bool
# window: Window
# karel: Karel
# karel_map: RectangleMap
# argv: Namespace
#
# def startup_karel():
#     global karel, karel_map, window, argv, ignore_robot_errors

karel = karel_map = window = None
argv = parser.parse_args()
ignore_robot_errors = argv.ignore_robot_errors

if argv.karelpos is not None or argv.kareldir != ">":
    karel = Karel(position=argv.karelpos, facing=argv.kareldir)

# Board is loaded and starts the curses window
try:
    if argv.karelmap is not None:
        karel, karel_map = parse_map(
            path=argv.karelmap,
            karel=karel,
            no_error=argv.ignore_robot_errors,
            new_style_map=argv.new_style_map,
        )
        argv.x_map = len(karel_map[0])
        argv.y_map = len(karel_map)
    # Curse the window
    window = Window(
        karel=karel,
        tiles=karel_map,
        x_map=argv.x_map,
        y_map=argv.y_map,
        lookahead=argv.lookahead,
        speed=argv.speed,
    )
except IOError as e:
    print("Could not open karel map file:\n" + str(e), file=stderr)
    exit(ENOENT)
except RobotError as e:
    print("Failed parsing map:\n" + str(e), file=stderr)
    exit(EINVAL)
except BaseException as e:
    endwin()
    print("There was a problem with curses:\n" + str(e), file=stderr)
    raise e


###########################################################
#                     KAREL FUNCTIONS                     #
###########################################################


def status_line(command: str = ""):
    """ Unsafe print/log status line. """
    if argv.quiet and argv.logfile is None:
        return
    text = (
        f"{(*window.karel.position,)} "
        f"{repr(window.karel_tile)} "
        f"View{(*window.offset,)} "
        f"{command}"
    )
    if argv.logfile is not None:
        print(text, file=argv.logfile)
    if not argv.quiet:
        window.message(text)


# Movement
@screen(window, moved=True)
def move():
    """ Karel tries to move in the direction he is facing. """
    window.move()
    status_line("MOVE")


@screen(window)
def turn_left():
    """ Karel turns left. """
    window.karel.turn_left()
    status_line("TURN_LEFT")


@screen(window)
def turn_right():
    """ Karel turns right. """
    window.karel.turn_right()
    status_line("TURN_RIGHT")


# Beepers
@screen(window)
def pick_beeper():
    """ Karel tries to pick up a beeper. """
    window.pick_beeper()
    status_line("TAKE")


@screen(window)
def put_beeper():
    """ Karel puts down a beeper (if he has any). """
    window.put_beeper()
    status_line("PUT")


@screen(window, draw=None)
def beeper_is_present():
    """ True iff Karel stands on a beeper. """
    status_line("IFMARK")
    return window.beeper_is_present()


# Walls
@screen(window, draw=None)
def front_is_blocked():
    """ True iff Karel can't move forward. """
    status_line("IFWALL")
    return window.front_is_blocked()


@screen(window, draw=None)
def front_is_treasure():
    """ True iff Karel stands in front of a Treasure. """
    status_line("IFGOLD")
    return window.front_is_treasure()


# KAREL_DIR
def facing_north():
    """ True iff Karel is facing north (^). """
    return window.karel.facing_north()


def facing_south():
    """ True iff Karel is facing south (v). """
    return window.karel.facing_south()


def facing_east():
    """ True iff Karel is facing east (>). """
    return window.karel.facing_east()


def facing_west():
    """ True iff Karel is facing west (<). """
    return window.karel.facing_west()


# Execution
def set_speed(spd):
    """ Set the number of ticks per second. """
    window.speed = spd


def toggle_status_line(quiet=None):
    """ If true then quiet status-line, on None return current. """
    if quiet is None:
        return argv.quiet
    argv.quiet = quiet
    return argv.quiet


def set_karel_beepers(b=0):
    """ Set Karel's beepers, with None working as inf. """
    window.karel.beepers = b if b is None else max(0, round(b))


@screen(window, draw=None)
def pause():
    """ Pause execution, press any key to continue. """
    window.pause()


@screen(window, draw=None)
def screen_resize():
    window.screen_resize()
    status_line("RESIZE")


###########################################################
#             INTERACTIVE CLIENT FOR TESTING              #
###########################################################


@screen(window, draw=None)
def message(text="Press Q to quit, P to pause", color=None):
    window.message(text, color=color or window.Colors.exception)


@screen(window, draw=True)
def front_set_tile(tile):
    """ Set tile in front of Karel. """
    if not isinstance(tile, Tile):
        return ValueError(f"Can not set map Tile to {tile}")
    x, y = window.karel_pos
    xv, yv = window.karel.facing
    window.set_view(x + xv, y + yv, tile)
    status_line(f"SET {tile}")


def set_wall():
    front_set_tile(one_tile(Wall))


def set_tile():
    front_set_tile(one_tile(Empty))


def set_gold():
    front_set_tile(one_tile(Treasure))


def interactive():
    """ Command Karel on a Board using your keyboard. """

    screen(window)(status_line)("INTERACTIVE")
    outer_speed = window.speed
    set_speed(None)  # Human lives are too short

    class _InteractiveStop(Exception):
        pass

    def _interactive_stop():
        raise _InteractiveStop

    try:
        window.get_char(
            no_delay=False,
            handle={
                ord("q"): KeyHandle(repeat=False, handle=lambda: exit()),
                ord("u"): KeyHandle(repeat=True, handle=put_beeper),
                ord("i"): KeyHandle(repeat=True, handle=pick_beeper),
                ord("I"): KeyHandle(repeat=False, handle=_interactive_stop),
                ord("R"): KeyHandle(repeat=True, handle=screen_resize),
                ord("W"): KeyHandle(repeat=True, handle=set_wall),
                ord("T"): KeyHandle(repeat=True, handle=set_gold),
                ord("D"): KeyHandle(repeat=True, handle=set_tile),
                ord("V"): KeyHandle(
                    repeat=True, handle=lambda: toggle_status_line(quiet=False)
                ),
                KEY_LEFT: KeyHandle(repeat=True, handle=turn_left),
                KEY_RIGHT: KeyHandle(repeat=True, handle=turn_right),
                KEY_UP: KeyHandle(repeat=True, handle=move),
                KEY_RESIZE: KeyHandle(repeat=True, handle=screen_resize),
                KEY_HELP: KeyHandle(
                    repeat=True,
                    handle=lambda: message("Use arrows to move, pIck, pUt and Quit."),
                ),
            },
        )
    except _InteractiveStop:
        pass
    set_speed(outer_speed)


window.handle[ord("I")] = KeyHandle(repeat=False, handle=interactive)


if __name__ == "__main__":
    interactive()
