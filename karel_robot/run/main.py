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
from ..parsers.interpret import Program, Commands, Conditions
from .interactive import *

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
        conditions=Conditions(ifwall=front_is_blocked, ifmark=beeper_is_present,),
        confirm=out if argv.wait else None,
    )
    status_line("LOADED PROGRAM", force=True)
    p.run()
    argv.program.close()


def main():
    """ The function to be executed as a script. """
    if argv.program:
        run_program()
    interactive()


if __name__ == "__main__":
    main()
