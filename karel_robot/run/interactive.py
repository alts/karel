from curses import KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_HELP, KEY_RESIZE
from typing import Optional
from .. import Tile, Empty, Beeper, Wall, Treasure, KeyHandle, KeysHandler
from .functions import *


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
        status_line(f"SET {tile}", color=window.Colors.empty)

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


class InteractiveStop(Exception):
    pass


def interactive_stop():
    raise InteractiveStop()


def interactive():
    """ Command Karel on a Board using your keyboard. """

    screen(window)(status_line)("INTERACTIVE", force=True)
    outer_speed = window.speed
    set_speed(-1)  # Human lives are too short

    handler: KeysHandler = {
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
        ord("I"): KeyHandle(repeat=False, handle=interactive_stop),
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
        handler[ord("0") + i] = KeyHandle(repeat=True, handle=karel_tile_beepers(i))

    try:
        window.get_char(no_delay=False, handle=handler)
    except InteractiveStop:
        pass
    set_speed(outer_speed)
