from curses import endwin
from errno import EINVAL, EIO
from sys import stderr
from argparse import FileType, Namespace, ArgumentParser
from typing import Optional
import os.path

from .. import Window, Karel, MapType, RobotError
from ..parsers import get_parser, MapParser


##############################################################################
#                               KAREL START-UP                               #
##############################################################################


def parser_add_program(parser: ArgumentParser):
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


def get_cli_arguments() -> Namespace:
    parser: ArgumentParser = get_parser()
    if __name__ == "__main__" or __name__.startswith("karel_robot.run"):
        parser_add_program(parser)
    return parser.parse_args()


def try_end_window(exception):
    try:
        endwin()
    except BaseException:
        print("Exception unrelated to screen was raised:", file=stderr)
        raise exception


def setup_window(cli_args: Namespace) -> Window:
    karel: Optional[Karel] = None
    karel_map: Optional[MapType] = None
    window_opt: Optional[Window] = None

    if cli_args.karelpos or cli_args.kareldir:
        karel = Karel(position=cli_args.karelpos, facing=cli_args.kareldir or ">")

    # Board is loaded and starts the curses window
    try:
        if cli_args.karelmap is not None:
            new_style = os.path.splitext(cli_args.karelmap.name)[1] == ".km2"
            m = MapParser(
                lines=cli_args.karelmap,
                karel=karel,
                new_style_map=cli_args.new_style_map or new_style,
            )
            karel, karel_map = m.karel, m.karel_map
            cli_args.karelmap.close()

            # overwrite default '-x' if not set or if '-X' was set
            if not cli_args.x_map or cli_args.infinite_x:
                cli_args.x_map = None if cli_args.infinite_x else m.width
            if not cli_args.y_map or cli_args.infinite_y:
                cli_args.y_map = None if cli_args.infinite_y else m.height
        # Curse the window
        window_opt = Window(
            karel=karel,
            tiles=karel_map,
            x_map=cli_args.x_map,
            y_map=cli_args.y_map,
            lookahead=cli_args.lookahead,
            speed=cli_args.speed,
            output=cli_args.output,
        )

        if cli_args.beepers is not None:
            window_opt.karel.beepers = cli_args.beepers
    except RobotError as e:
        try_end_window(exception=e)
        print("Failed setting up the map:\n" + str(e), file=stderr)
        exit(EINVAL)
    except BaseException as e:
        try_end_window(exception=e)
        print("Probably a problem with curses window:\n" + str(e), file=stderr)
        exit(EIO)

    if window_opt is None:
        print("Failed setting up the curses window", file=stderr)
        exit(EINVAL)  # Never happens, right?

    return window_opt
