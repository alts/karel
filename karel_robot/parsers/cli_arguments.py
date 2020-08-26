# Copied from 'karel_run.py'
""" Karel implementation in Python (with curses).

As a standalone app, this script opens a map and lets the user control Karel
using a keyboard. A custom map and other options may be specified.

Write your Karel program in Python by importing karel_robot.run and using the
simple functions like move() and turn_left(). Alternatively write recursive
(non Python) program and run it with 'karel --program example.ks'.

LICENSE

The karel_robot package is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

The karel_robot package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
the karel_robot package. If not, see `<https://www.gnu.org/licenses/>`_.
"""
from argparse import ArgumentParser, FileType


def get_parser() -> ArgumentParser:
    """ The command line argument parser used by karel executable
    and scripts importing karel_robot.run.
    """
    karel_doc, karel_license = map(lambda x: x.strip(), __doc__.split("LICENSE"))
    parser = ArgumentParser(
        description=karel_doc,
        epilog=karel_license,
        usage="%(prog)s [--help] [OPTIONS] [-m karel_map.km]",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="karel-robot 1.0",
        help="Show program's version number and exit.",
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
        "-X",
        "--infinite_x",
        action="store_true",
        help="Force infinite map in the x-dimension.",
    )
    parser.add_argument(
        "-Y",
        "--infinite_y",
        action="store_true",
        help="Force infinite map in the y-dimension.",
    )
    parser.add_argument(
        "-d",
        "--kareldir",
        metavar=">",
        help="The direction Karel starts with (one of > v < ^).",
    )
    parser.add_argument(
        "-k",
        "--karelpos",
        nargs=2,
        type=int,
        metavar="n",
        help="Sets the position Karel starts on.",
    )
    parser.add_argument(
        "-b",
        "--beepers",
        type=int,
        metavar="B",
        help="Sets the number of beepers Karel starts with.",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=3,
        metavar="S",
        help="Sets the number of ticks per second, 0 is no limit.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=0,
        dest="verbose",
        default=1,
        help="Hides the status line.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=2,
        default=1,
        help="Shows the status line and adds more info.",
    )
    parser.add_argument(
        "-l",
        "--logfile",
        type=FileType("a", bufsize=1),
        metavar="FILE.log",
        help="Writes logging information to the file (needs append permission).",
    )
    parser.add_argument(
        "-L",
        "--lookahead",
        default=1,
        type=int,
        metavar="L",
        help="Set the number of fields visible ahead of Karel.",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUT.km2",
        help="Set the output file, save it yourself (map must be finite).",
    )
    parser.add_argument(
        "-n",
        "--new_style_map",
        action="store_true",
        help="Map starts with 'KAREL X Y > B' and has spaces between tiles.",
    )
    parser.add_argument(
        "-m",
        "--karelmap",
        type=FileType("r"),
        metavar="MAP.km2",
        help="Text file with a map of karel world.",
    )
    return parser
