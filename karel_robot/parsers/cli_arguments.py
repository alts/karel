# Copied from 'karel_run.py'
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
from argparse import ArgumentParser, FileType, Namespace

def get_parser() -> ArgumentParser:
    karel_doc, karel_license = map(lambda x: x.strip(), __doc__.split("LICENSE"))
    parser = ArgumentParser(description=karel_doc, epilog=karel_license)
    parser.add_argument(
        "--version",
        action="version",
        version="karel-robot 1.0",
        help="Show program's version number and exit."
    )
    parser.add_argument(
        "-x",
        "--cols",
        dest="x_map",
        type=int,
        default=None,
        metavar="X",
        help="The width of the real map (default infinite).",
    )
    parser.add_argument(
        "-y",
        "--rows",
        dest="y_map",
        type=int,
        default=None,
        metavar="Y",
        help="The height of the real map (default infinite).",
    )
    parser.add_argument(
        "-d",
        "--kareldir",
        default=">",
        metavar=">",
        help="The direction Karel starts with (one of > v < ^).",
    )
    parser.add_argument(
        "-p",
        "--karelpos",
        nargs=2,
        type=int,
        metavar="X Y",
        help="The position Karel starts on.",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=3,
        metavar="S",
        help="Number of ticks per second.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="No status line shown. ",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_false",
        dest="quiet",
        help="Turn on status line (default in interactive).",
    )
    parser.add_argument(
        "--logfile",
        type=FileType("a", bufsize=1),
        metavar="F",
        help="Logging file path.",
    )
    parser.add_argument(
        "--ignore_robot_errors",
        action="store_true",
        help="Ignore RobotError in parsing and interactive mode.",
    )
    parser.add_argument(
        "-l",
        "--lookahead",
        default=1,
        metavar="L",
        help="Number of fields visible ahead of Karel.",
    )
    parser.add_argument(
        "-n", "--new_style_map",
        action="store_true",
        help="Map starts with 'KAREL X Y > B' and has spaces between tiles.",
    )
    parser.add_argument(
        "-m",
        "--karelmap",
        required=False,
        metavar="YOUR_WORLD.karelmap",
        help="Text file with a map of karel world (overwrites -x, -y).",
    )
    return parser
