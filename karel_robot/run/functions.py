from errno import EINVAL
from sys import stderr
from .. import Window, screen
from .startup import get_cli_arguments, setup_window

argv = get_cli_arguments()
window: Window = setup_window(cli_args=argv)


##############################################################################
#                                STATUS LINE                                 #
##############################################################################


def status_line(command: str = "", force: bool = False, color=None):
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
        window.message(text, color=color)


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
def set_speed(speed: float):
    """ Set the number of ticks per second. """
    window.speed = max(0.0, speed) or None


def set_beepers(b: int = 0):
    """ Set Karel's beepers, with None working as inf. """
    window.karel.beepers = None if b is None else max(0, int(b))


@screen(window, draw=None)
def pause():
    """ Pause execution, press any key to continue. """
    window.pause()


@screen(window, draw=None)
def screen_resize():
    """ Window readjusts self to include Karel on board. """
    window.resize()
    status_line("RESIZE")
