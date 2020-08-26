r""" This file is part of karel_robot package.

Window to Karel's world
=======================

This file defines the manager class Window, that draws the board
on screen and shows messages to the user on the bottom line.

See the README in the package root folder for general take and the
one in this folder for details.


LICENSE
^^^^^^^

A GPLv3/later license applies::

    The karel_robot package is free software: you can redistribute it
    and/or modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation, either version 3
    of the License, or (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the karel_robot package.
If not, see `<https://www.gnu.org/licenses/>`_.
"""
from __future__ import annotations
import io
import curses
from functools import wraps
from time import sleep
from typing import Callable, Any, NamedTuple, Dict, Optional
from .robot import Karel, RobotError
from .tiles import Beeper, Wall, Treasure
from .board import BoardView, MapType


class KeyHandle(NamedTuple):
    """ Response to user pressing key. """

    repeat: bool
    handle: Callable[[], Any]


KeysHandler = Dict[int, KeyHandle]
""" Dictionary for specifying response to user keypress. """


class Window(BoardView):
    """ Cursed window that draws a Board and interacts with user.

    Note that the curses screen is started on `__init__`.
    """

    # all colors are set in `start_screen`
    class Colors:
        """ Curses colors for printing in terminal. """

        wall: int
        empty: int
        karel: int
        beeper: int
        karel_beeper: int
        exception: int
        complete: int
        clear: int

    def __init__(
        self,
        karel: Optional[Karel] = None,
        tiles: Optional[MapType] = None,
        x_map: Optional[int] = None,
        y_map: Optional[int] = None,
        speed: Optional[float] = 2.0,
        lookahead: int = 1,
        output: Optional[str] = None,
    ):
        """
        Args:
            karel (Karel): The robot or default Karel if None.
            x_map: The x_view of the map.
            y_map: The y_view of the map.
            tiles (Optional[Any]): Mutable map supporting tiles[y_map][x_map],
                   like list or dict (if dict then indices
                   not in tiles are considered Tile).
            speed: The number of ticks per second.
            lookahead: The number of fields visible ahead of Karel.

        Description copied from :class:`BoardView`, :class:`Board`
        and :class:`KarelMap`.
        """
        super().__init__(
            x_view=-1,  # set later
            y_view=-1,  # set later
            x_map=x_map,
            y_map=y_map,
            karel=karel,
            tiles=tiles,
            lookahead=lookahead,
        )
        self.speed: Optional[float] = max(0.0, speed) or None
        """ The number of ticks per second, ``None`` meaning no wait. """

        self.screen = curses.initscr()
        """ Cursed screen representing the whole terminal window. """
        self._del_screen = True  # Mark for cleanup: curses screen initialized
        # ---------------------- #

        self.y_screen, self.x_screen = self.screen.getmaxyx()
        """ Dimension of the whole terminal screen. """

        self.setup_screen()
        self._del_setup = True  # Mark for cleanup: curses screen setup
        # --------------------- #

        # reset the view dimensions, now that we know screen
        x, y = self.get_board_size()
        self.x_view = x
        """ The width of the board view (without border) """
        self.y_view = y
        """ The height of the board view (without border) """

        self.output: Optional[str] = output
        # NOTE: sub-windows share with parent the same positions, no overlay
        self.board_win = self.screen.subwin(self.y_view + 2, self.x_view + 2, 0, 0)
        """ The sub-window where Karel and his board is drawn """

        self.message_win = curses.newwin(1, self.x_screen, self.y_screen - 1, 0)
        """ The sub-window where messages to user are printed """
        self._last_message_len = 0

        self.handle: KeysHandler = {
            ord("q"): KeyHandle(repeat=False, handle=lambda: exit()),
            ord("p"): KeyHandle(repeat=False, handle=self.pause),
            curses.KEY_RESIZE: KeyHandle(repeat=True, handle=self.resize),
        }
        """ What to do on user response, in ``key:(retry, function)`` format """

        self.resize()  # why again?
        self.no_complete = False
        """ Flag for complete message being shown """

    def draw(self) -> int:
        """ Draw the whole board. """
        self.board_win.border()
        for y in range(self.y_view):
            for x in range(self.x_view):
                self.draw_tile(x, y)

        self.draw_karel_tile()
        self.board_win.refresh()
        return self.get_char(no_delay=True, handle=self.handle)

    def redraw(self, moved=False) -> int:
        """ Redraw Karel's tile and the one he `moved` from."""
        self.draw_karel_tile(moved).board_win.refresh()
        return self.get_char(no_delay=True, handle=self.handle)

    def pause(self):
        """ Wait for keypress. """
        self.draw_exception("PAUSED")

    def move(self):
        """ Move Karel inside view and if he were to leave the screen,
            move it too.
        """
        if super(Window, self).move().advanced:
            self.draw()

    # IMPLEMENTATION DETAILS ########################################

    def setup_screen(self):
        """ Initialize cursed screen. """
        curses.noecho()  # turn off automatic echoing of keys to the screen
        curses.cbreak()  # react to keys instantly
        self.screen.keypad(True)  # curses process special keys
        curses.curs_set(False)  # make cursor invisible
        self.screen.timeout(1)
        self.setup_colors()

    def setup_colors(self):
        """ Setup curses colors and store them in :class:`Window.Colors`. """
        curses.start_color()
        # Window attribute : (Color foreground, optional Color background)
        colors = {
            "wall": (curses.COLOR_WHITE, curses.COLOR_WHITE),
            "empty": (curses.COLOR_YELLOW, None),
            "karel": (curses.COLOR_CYAN, None),
            "beeper": (curses.COLOR_GREEN, None),
            "karel_beeper": (curses.COLOR_RED, None),
            "exception": (curses.COLOR_RED, None),
            "complete": (curses.COLOR_GREEN, None),
            "clear": (curses.COLOR_BLACK, None),
        }
        for i, (attr, (col_fg, col_bg)) in enumerate(colors.items(), start=1):
            curses.init_pair(i, col_fg, col_bg or curses.COLOR_BLACK)
            setattr(self.Colors, attr, curses.color_pair(i))

    def resize(self):
        """ Recalculate the screen dimensions and draw the board again. """
        # TODO: check why ERR on positive coordinates
        sleep(1 / 5)
        self.board_win.clear()
        self.message_win.clear()
        self.y_screen, self.x_screen = self.screen.getmaxyx()
        self.x_view, self.y_view = self.get_board_size()
        self.board_win.resize(self.y_view + 2, self.x_view + 2)
        self.message_win.mvwin(self.y_screen - 1, 0)
        self.message_win.resize(1, self.x_screen)
        self.message_win.refresh()
        self.reset_offset()
        self.draw()

    def get_char(self, no_delay=True, restore=False, handle: KeysHandler = None) -> int:
        """ Wait for and then return user input - optionally handle it first. """

        def handle_char(char) -> bool:
            """ Run handling function and return whether input should be read again. """
            ch_to_handle = char if char in handle else curses.KEY_HELP
            if ch_to_handle not in handle:
                return False
            handle[ch_to_handle].handle()
            return handle[ch_to_handle].repeat

        while True:
            self.screen.nodelay(no_delay)
            if no_delay:
                self.wait()
            ch = self.screen.getch()
            self.screen.nodelay(restore)
            if handle and handle_char(ch):
                continue
            return ch

    def wait(self):
        """ If speed set, then wait for `1/speed` of a second. """
        if self.speed is not None:
            sleep(1 / self.speed)
        return self

    def get_board_size(self):
        # TODO
        """

        Note: self.*_screen must be set!

        :return: the size of view without border
        """
        y_view = self.y_screen - 3  # one line for messages
        x_view = self.x_screen - 2  # and two for border
        if y_view < 1 or x_view < 1:
            raise RuntimeError(
                "Screen too small "
                f"{self.x_screen, self.y_screen} "
                f"for board {self.karel_map.x, self.karel_map.y} "
                "Minimum: 3columns 4rows"
            )
        if self.karel_map.y:
            y_view = min(self.karel_map.y, y_view)
        if self.karel_map.x:
            x_view = min(self.karel_map.x, x_view)
        return x_view, y_view

    # DRAWING #######################################################

    def draw_tile(self, x, y):
        """ Draw the tile on (x_map, y_map). """
        tile = self.get_view(x, y)
        if isinstance(tile, Wall):
            color = self.Colors.wall
        elif isinstance(tile, (Beeper, Treasure)):
            color = self.Colors.beeper
        else:
            color = self.Colors.empty
        self.board_win.addch(y + 1, x + 1, str(tile), color)
        return self

    def draw_karel_tile(self, moved=False):
        """ Draw the tile Karel is standing on and the one he ``moved`` from. """
        color = (
            self.Colors.karel_beeper if self.beeper_is_present() else self.Colors.karel
        )
        try:
            self.board_win.addch(
                self.karel_pos.y + 1,  # 1 border line
                self.karel_pos.x + 1,
                self.karel.to_dir(),
                color,
            )
        except curses.error:
            raise RobotError(
                f"Could not draw Karel's tile {self.karel_pos}, "
                f"direction {self.karel.to_dir()} and color {color} "
                f"in view {self.x_view, self.y_view}"
            )

        if moved:
            x, y = self.karel_pos
            vx, vy = self.karel.facing
            self.draw_tile(x - vx, y - vy)
        return self

    def draw_exception(self, exception):
        """ Draw exception and wait for keypress.

        :raises SystemExit: exits the program if user presses the Q key
        """
        curses.beep()
        self.message(str(exception), self.Colors.exception, pause=True)
        self.message("")

    def message(self, text: str, color: int = None, pause: bool = False):
        """ Draw text to user. """
        if color is None:
            color = self.Colors.karel
        if pause:
            text = text + " Press any key to continue"
        self.message_win.insertln()
        if text:
            self.message_win.addstr(0, 0, text[: self.x_screen], color)
        self.message_win.refresh()
        if pause:
            handle = self.handle.copy()
            del handle[ord("p")]
            self.get_char(no_delay=False, handle=handle)

    def save(self):
        # TODO
        if not self.output:
            return self.draw_exception("Can not save Map without specified output.",)
        try:
            with io.open(self.output, mode="w") as output:
                c_max = self.karel_map.max_coordinate(default=self.karel.position)
                c_min = self.karel_map.min_coordinate(default=self.karel.position)
                print(  # Header
                    f"KAREL "
                    f"{self.karel.position.x - c_min.x} "
                    f"{self.karel.position.y - c_min.y} "
                    f"{self.karel.to_dir()} "
                    f"{'N' if self.karel.beepers is None else self.karel.beepers} ",
                    file=output,
                )
                for y in range(c_min.y, c_max.y + 1):  # Tiles
                    line = (self.karel_map[x, y] for x in range(c_min.x, c_max.x + 1))
                    print(" ".join(map(str, line)), file=output)
        except IOError:
            self.draw_exception(f"Output to file {self.output} failed.")
        else:
            self.message(f"Saved the map to {self.output}.")

    def close_screen(self):
        """ DO NOT USE WINDOW AFTER THIS! """
        if hasattr(self, "no_complete") and not self.no_complete:
            self.no_complete = True
            self.message("Program Complete! Press any key to exit")
            self.get_char(no_delay=False)
        if hasattr(self, "_del_setup") and self._del_setup:
            # reverse curses terminal settings
            self._del_setup = False
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
        if hasattr(self, "_del_screen") and self._del_screen:
            # restore terminal
            self._del_screen = False
            curses.endwin()

    def __del__(self):
        """ Show complete text and close screen on program end.
        """
        self.close_screen()


class WindowOpen:
    """ Window manager to be used like ``open``.

    Usage::

        with WindowOpen(x_map=1, y_map=1) as w:
           w.move()
           # ...
    """

    def __init__(
        self,
        karel: Optional[Karel] = None,
        tiles: Optional[MapType] = None,
        x_map: Optional[int] = None,
        y_map: Optional[int] = None,
        speed: Optional[float] = 2.0,
        lookahead: int = 1,
        output: Optional[str] = None,
    ):
        """ Description copied from :class:`Window`.

        Args:
            karel (Karel): The robot or default Karel if None.
            x_map: The x_view of the map.
            y_map: The y_view of the map.
            tiles (Optional[Any]): Mutable map supporting tiles[y_map][x_map],
                   like list or dict (if dict then indices
                   not in tiles are considered Tile).
            speed: The number of ticks per second.
            lookahead: The number of fields visible ahead of Karel.
            output: The path to file where map can be saved.

        Returns:
            A :class:`Window` instance, that when exiting ``with`` block
            will optionally save the map to ``output`` and close screen.

        """
        self._w = Window(karel, tiles, x_map, y_map, speed, lookahead, output)

    def __enter__(self):
        return self._w

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._w.no_complete = exc_type is not None
        # curses error is BaseException, can't do anything with that
        if exc_type is None or issubclass(exc_type, Exception):
            if self._w.output is not None:
                self._w.save()
            self._w.draw_exception(exc_val)
        self._w.close_screen()
        return False


def screen(  # noqa: C901
    win: Window, moved: bool = False, draw: Optional[bool] = False
):
    """ Safely execute function and redraw.

    Use this when the window should stay open upon success.

    Args:
        win: The window managing screen.
        moved: Whether Karel has moved (redraws last tile).
        draw: Draw whole screen (None means no drawing and False means redraw).
    Returns:
        Wrapper to safely execute function func.
    """
    if not isinstance(win, Window):
        raise RobotError("Supplied window is not a Window object, not initialized?")

    def dec_refresh(func):
        """ Inner decorator that only takes function and safely executes it. """

        @wraps(func)
        def wrap_refresh(*args, **kwargs):
            """ The actual wrapper for function working with Window. """
            try:
                result = func(*args, **kwargs)
                if draw is True:
                    win.draw()
                elif draw is False:
                    win.redraw(moved)
                return result
            except RobotError as ex:
                try:
                    win.draw_exception(ex)
                except BaseException as ex:
                    win.no_complete = True
                    win.close_screen()
                    raise ex
            except BaseException as ex:
                win.no_complete = True
                win.close_screen()
                raise ex

        return wrap_refresh

    return dec_refresh
