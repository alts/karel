#!/usr/bin/env python3
""" Karel implementation in Python (with curses).

==============================================================================
                             Run Karel the Robot
==============================================================================

As a standalone app, this script opens a map and lets the user control Karel
using a keyboard. A custom map and other options may be specified.

Write your Karel program in Python by importing karel_robot.run and using the
simple functions like move() and turn_left(). Alternatively write recursive
(non Python) programs and run them with '--program example.ks'. See Examples.


==============================================================================
                                   Examples
==============================================================================

Following examples assume you are running karel from terminal and have Python
version at least 3.6 installed.

- **Command Karel using keyboard in a infinite empty world**::

    karel

- **Write a simple Python script commanding Karel**::

    from karel_robot.run import *
    # moves to the wall, places one beeper and stops
    while not front_is_blocked():
        move()
    put_beeper()

  Then run Karel in a 10x10 world like this::

    python3 programs/walk.py -x 10 -y 10

- **Write a recursive Karel program as a challenge**::

    DEFINE MAIN
        IFWALL PUT MOVE
        IFWALL SKIP MAIN
    END
    RUN MAIN

  Run Karel in a one line 200 squares long world::

    karel --program programs/easy/1_walk.ks -y 1 -x 200

  > For details see the karel_robot/parsers/interpret.py file.


------------------------------------------------------------------------------
                                     Note
------------------------------------------------------------------------------

The curses screen starts up upon import and closes on error or program end.


------------------------------------------------------------------------------
                              Exported functions
------------------------------------------------------------------------------

You can use simple functions in Python programs importing karel_robot.run:

======================== ===================================================
        Movement
======================== ===================================================
``move()``               Karel moves in the direction he is facing
``turn_left()``          Karel turns left
``turn_right()``         Karel turns right
======================== ===================================================

======================== ===================================================
        Beepers
======================== ===================================================
``pick_beeper()``        Karel tries to pick up a beeper
``put_beeper()``         Karel puts down a beeper (if he has any)
``beeper_is_present()``  True iff Karel stands on a beeper
======================== ===================================================

======================== ===================================================
         Walls
======================== ===================================================
``front_is_blocked()``   True iff Karel can't move forward
``front_is_treasure()``  True iff Karel stands in front of a Treasure
======================== ===================================================

======================== ===================================================
       Direction
======================== ===================================================
``facing_north()``       True iff Karel is facing north (``^``)
``facing_south()``       True iff Karel is facing south (``v``)
``facing_east()``        True iff Karel is facing east (``>``)
``facing_west()``        True iff Karel is facing west (``<``)
======================== ===================================================

========================= ==================================================
       Execution
========================= ==================================================
``set_beepers(None)``     Set Karel's beepers (``None`` is ∞)
``set_speed(100)``        Set how fast Karel moves, 0 to 100
``pause()``               Pause execution and wait for user
``message(text, pause)``  Show message to user and if ``pause`` wait.
``write_map(path)``       Writes the map (must be finite) to a file
``exit()``                End execution
========================= ==================================================

For details see the section of the file marked 'KAREL FUNCTIONS'.


==============================================================================
                                   LICENSE
==============================================================================

The karel_robot package is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

The karel_robot package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
the karel_robot package. If not, see `<https://www.gnu.org/licenses/>`_.
"""
from curses import endwin, KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_HELP, KEY_RESIZE
from errno import EINVAL, EIO
from sys import stderr
from argparse import FileType
from typing import Optional
import os.path

from .. import *
from ..parsers import *


##############################################################################
#                               KAREL START-UP                               #
##############################################################################

parser = get_parser()

if __name__ in ["__main__", "karel_robot.run.main"]:
    if parser.usage:
        parser.usage += " [-p program.ks]"
    parser.add_argument(
        "-W",
        action="count",
        dest="wait",
        default=0,
        help="Waits for user keypress when stepping through --program. "
        "On two or more (-WW) shows the info, but do not wait for confirmation. "
        "On three or more (-WWW) writes only program message to --logfile. ",
    )
    parser.add_argument(
        "-p",
        "--program",
        type=FileType("r"),
        metavar="karel_program.ks",
        help="Parse and run text file with a (non Python) recursive Karel program.",
    )

_karel: Optional[Karel] = None
_karel_map: Optional[MapType] = None

window_opt: Optional[Window] = None
argv = parser.parse_args()

if argv.karelpos or argv.kareldir:
    _karel = Karel(position=argv.karelpos, facing=argv.kareldir or ">")

# Board is loaded and starts the curses window
try:
    if argv.karelmap is not None:
        _new_style = os.path.splitext(argv.karelmap.name)[1] == ".km2"
        _m = MapParser(lines=argv.karelmap, karel=_karel, new_style_map=argv.new_style_map or _new_style)
        _karel, _karel_map = _m.karel, _m.karel_map
        argv.karelmap.close()
        # overwrite default '-x' if not set or if '--ix' was set
        if not argv.x_map or argv.infinite_x:
            argv.x_map = None if argv.infinite_x else _m.width
        if not argv.y_map or argv.infinite_y:
            argv.y_map = None if argv.infinite_y else _m.height
    # Curse the window
    window_opt = Window(
        karel=_karel,
        tiles=_karel_map,
        x_map=argv.x_map,
        y_map=argv.y_map,
        lookahead=argv.lookahead,
        speed=argv.speed,
        output=argv.output,
    )
    if argv.beepers is not None:
        window_opt.karel.beepers = argv.beepers
except RobotError as e:
    print("Failed setting up the map:\n" + str(e), file=stderr)
    exit(EINVAL)
except BaseException as e:
    try:
        endwin()
    except BaseException:
        print("Exception unrelated to screen was raised:", file=stderr)
        raise e
    print("Probably a problem with curses window:\n" + str(e), file=stderr)
    exit(EIO)


if window_opt is None:
    print("Failed setting up the curses window", file=stderr)
    exit(EINVAL)  # Never happens, right?

window: Window = window_opt


##############################################################################
#                                STATUS LINE                                 #
##############################################################################


def status_line(command: str = "", force=False):
    """ Unsafe print/log status line. """
    if argv.verbose == 0 and not argv.logfile and not force:
        return

    karel = window.karel
    if not karel:
        print("Karel left the screen!", file=stderr)  # never happens, right?
        exit(EINVAL)

    text = (
        f"{command.ljust(5) if command else ''} "
        f"{(*karel.position,)} "
        f"{repr(window.karel_tile)} "
    )
    if argv.verbose == 2:
        text += f"View{(*window.offset,)} "
    if argv.logfile and (force or argv.wait != 3):
        print(text, file=argv.logfile)
    if force or argv.verbose and not (argv.program and argv.wait):
        window.message(text)


@screen(window, draw=True)
def toggle_status_line(status=None):
    """ Return current status line setting and set to next one or custom. """
    v = argv.verbose
    argv.verbose = (v + 1) % 3 if status is None else status
    status_line(f"TOGGLE{v}")
    return v


##############################################################################
#                              KAREL FUNCTIONS                               #
##############################################################################

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
    status_line("LEFT")


@screen(window)
def turn_right():
    """ Karel turns right. """
    window.karel.turn_right()
    status_line("RIGHT")


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
    status_line("IF_MARK")
    return window.beeper_is_present()


# Walls
@screen(window, draw=None)
def front_is_blocked():
    """ True iff Karel can't move forward. """
    status_line("IF_WALL")
    return window.front_is_blocked()


@screen(window, draw=None)
def front_is_treasure():
    """ True iff Karel stands in front of a Treasure. """
    status_line("IF_GOLD")
    return window.front_is_treasure()


# KAREL_DIR
@screen(window, draw=None)
def facing_north():
    """ True iff Karel is facing north (^). """
    status_line("IF_NORTH")
    return window.karel.facing_north()


@screen(window, draw=None)
def facing_south():
    """ True iff Karel is facing south (v). """
    status_line("IF_SOUTH")
    return window.karel.facing_south()


@screen(window, draw=None)
def facing_east():
    """ True iff Karel is facing east (>). """
    status_line("IF_EAST")
    return window.karel.facing_east()


@screen(window, draw=None)
def facing_west():
    """ True iff Karel is facing west (<). """
    status_line("IF_WEST")
    return window.karel.facing_west()


# Execution
def set_speed(spd):
    """ Set the number of ticks per second. """
    window.speed = spd


def set_beepers(b=0):
    """ Set Karel's beepers, with None working as inf. """
    window.karel.beepers = None if b is None else max(0, int(b))


@screen(window, draw=None)
def pause():
    """ Pause execution, press any key to continue. """
    window.pause()


@screen(window, draw=None)
def screen_resize():
    """ Window readjusts self to include Karel on board. """
    window.screen_resize()
    status_line("RESIZE")


##############################################################################
#                                   OUTPUT                                   #
##############################################################################


@screen(window, draw=None)
def message(text="Press Q to quit, P to pause", paused=False, *, color=None):
    """ Show message to user in the message window (bottom line). """
    window.message(text, color=color, pause=paused)


@screen(window, draw=None)
def write_map(filepath: Optional[str] = None):
    """ Save map to file, if map is not infinite and user can write to file. """
    o = window.output
    if filepath:
        window.output = filepath
    window.save()
    window.output = o


##############################################################################
#                                   CHEATS                                   #
##############################################################################


def front_set_tile(tile):
    """ Set tile in front of Karel. """
    @screen(window, draw=True)
    def _front_set_tile():
        if not isinstance(tile, Tile):
            return ValueError(f"Can not set map Tile to {tile}")
        window.karel_facing = tile
        status_line(f"SET {tile}")
    return _front_set_tile


def karel_tile_beepers(n: int):
    """ Set the tile Karel is standing on to include exactly `n` beepers. """
    @screen(window)
    def _karel_tile_beepers():
        """ Set the tile Karel stands on to exactly `n` beepers. """
        if n < 1:
            window.karel_tile = Empty()
        else:
            window.karel_tile = Beeper(count=n)
        status_line(f"SET{n}")
    return _karel_tile_beepers


##############################################################################
#                              INTERACTIVE MODE                              #
##############################################################################

def interactive():
    """ Command Karel on a Board using your keyboard. """

    screen(window)(status_line)("INTERACTIVE", force=True)
    outer_speed = window.speed
    set_speed(None)  # Human lives are too short

    class _InteractiveStop(Exception):
        pass

    def _interactive_stop():
        raise _InteractiveStop

    handle = {
        # basic commands
        KEY_LEFT: KeyHandle(repeat=True, handle=turn_left),
        KEY_RIGHT: KeyHandle(repeat=True, handle=turn_right),
        KEY_UP: KeyHandle(repeat=True, handle=move),
        ord("q"): KeyHandle(repeat=False, handle=lambda: exit()),
        ord("u"): KeyHandle(repeat=True, handle=put_beeper),
        ord("i"): KeyHandle(repeat=True, handle=pick_beeper),
        # save
        ord("w"): KeyHandle(repeat=True, handle=write_map),
        # set tiles
        ord("#"): KeyHandle(repeat=True, handle=front_set_tile(Wall())),
        ord("."): KeyHandle(repeat=True, handle=front_set_tile(Empty())),
        ord("$"): KeyHandle(repeat=True, handle=front_set_tile(Treasure())),
        # stop interactive only
        ord("I"): KeyHandle(repeat=False, handle=_interactive_stop),
        # change verbosity
        ord("V"): KeyHandle(repeat=True, handle=toggle_status_line),
        # resize screen
        ord("R"): KeyHandle(repeat=True, handle=screen_resize),
        KEY_RESIZE: KeyHandle(repeat=True, handle=screen_resize),
        # user help
        KEY_HELP: KeyHandle(
            repeat=True,
            handle=lambda: message("Use arrows to move, i/u/q to pIck, pUt and Quit."),
        ),
    }
    for i in range(10):
        handle[ord('0') + i] = KeyHandle(repeat=True, handle=karel_tile_beepers(i))

    try:
        window.get_char(no_delay=False, handle=handle)
    except _InteractiveStop:
        pass
    set_speed(outer_speed)


window.handle[ord("I")] = KeyHandle(repeat=False, handle=interactive)


@screen(window, draw=None)
def run_program():
    """ Parse recursive Karel program and run it.
    """
    status_line("PARSING PROGRAM", force=True)

    def out(m):
        """ Tee to logfile if set. """
        if argv.wait:
            message(m, paused=argv.wait == 1)
        if argv.logfile:
            print(m, file=argv.logfile)

    p = Program(
        lines=argv.program,
        commands=Commands(
            skip=lambda: None,
            move=move,
            left=turn_left,
            right=turn_right,
            pick=pick_beeper,
            put=put_beeper,
        ),
        conditions=Conditions(
            ifwall=front_is_blocked,
            ifmark=beeper_is_present,
        ),
        confirm=out if argv.wait else None,
    )
    status_line("LOADED PROGRAM", force=True)
    p.run()
    argv.program.close()
    argv.program = None


def main():
    """ The function to be executed as a script. """
    if argv.program:
        run_program()
    interactive()


if __name__ == "__main__":
    main()
