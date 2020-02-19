""" Window, the class that draws the board on screen.

Start Karel program with `from karel_robot.run import *` instead.
For more details see README.
"""
import curses
import time

from .world import *


class Window(World):
    """Cursed window that draws a Board.

    Note that the curses screen is started on `__init__`.
    """

    MAX_SPEED = 100.0

    COLORS = {  # Window attribute : (color foreground, background)
        'color_clear': (curses.COLOR_BLACK, None),
        'color_wall': (curses.COLOR_WHITE, curses.COLOR_WHITE),
        'color_empty': (curses.COLOR_YELLOW, None),
        'color_karel': (curses.COLOR_CYAN, None),
        'color_beeper': (curses.COLOR_GREEN, None),
        'color_karel_beeper': (curses.COLOR_RED, None),
        'color_exception': (curses.COLOR_RED, None),
        'color_complete': (curses.COLOR_GREEN, None)
    }

    def __init__(self, karel, karel_map, speed=(MAX_SPEED / 2)):
        super(Window, self).__init__(karel, karel_map)
        self.screen = None
        self.speed = self.valid_speed(speed)
        # all colors are set in start screen
        self.color_clear = None
        self.color_wall = None
        self.color_empty = None
        self.color_karel = None
        self.color_beeper = None
        self.color_karel_beeper = None
        self.color_exception = None
        self.color_complete = None
        self.start_screen()
        self.draw()

    def start_screen(self):
        """Start curses screen and set colors. """
        self.screen = curses.initscr()
        self.board_fits(throw=True)
        curses.start_color()
        for i, (attr, (col_fg, col_bg)) in enumerate(self.COLORS.items()):
            curses.init_pair(i + 1, col_fg, (curses.COLOR_BLACK if col_bg is None else col_bg))
            setattr(self, attr, curses.color_pair(i + 1))

    def board_fits(self, throw=False):
        """Check the board fits the window.
        :raises: RobotError if `throw` is True and board does not fit
        """
        screen_y, screen_x = self.screen.getmaxyx()
        fits = screen_y > self.height and screen_x >= self.width
        if not fits and throw:
            raise RobotError("Window too small ({}, {}) and World too big ({}, {} + 1)"
                             .format(screen_x, screen_y, self.width, self.height))
        return fits

    def valid_speed(self, speed):
        """Return the speed in `(0, MAX_SPEED)` or either end. """
        if speed < 0:
            return 0
        if speed > self.MAX_SPEED:
            return self.MAX_SPEED
        return speed

    def wait(self):
        """Wait for `(m-x)/m` seconds. """
        time.sleep((self.MAX_SPEED - self.speed) / self.MAX_SPEED)

    def draw_tile(self, column, row, tile):
        """Draw the tile on (column, row). """
        if isinstance(tile, Wall):
            color = self.color_wall
        elif isinstance(tile, (Beeper, Treasure)):
            color = self.color_beeper
        else:
            color = self.color_empty
        self.screen.addstr(row, column, str(tile), color)
        return self

    def draw_karel_tile(self, moved=False):
        """Draw the tile Karel is standing on and the one he `moved` from. """
        self.screen.addstr(
            self.karel.position[1],
            self.karel.position[0],
            self.karel.to_dir(),
            self.color_karel_beeper if self.beeper_is_present() else self.color_karel
        )
        if moved:
            x, y = self.karel.position
            vx, vy = self.karel.facing
            self.draw_tile(x - vx, y - vy, self.map[y - vy][x - vx])
        return self

    def screen_finalize(self):
        """Keep cursor below and check for user ending/pausing program.
        :exception: exits the program if user presses 'Q'
        """
        self.screen.addstr(self.height + 1, 0, ' ')
        self.screen.refresh()
        # quit if user presses 'q'
        self.screen.nodelay(True)
        self.wait()
        ch = self.screen.getch()
        self.screen.nodelay(False)
        if ch != -1 and chr(ch) == 'q':
            exit()
        if ch != -1 and chr(ch) == 'p':
            self.pause()
        return self

    def draw(self):
        """Draw the whole board. """
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                self.draw_tile(x, y, tile)
        self.draw_karel_tile()
        return self.screen_finalize()

    def redraw(self, moved=False):
        """Redraw Karel's tile and the one he `moved` from."""
        self.draw_karel_tile(moved)
        return self.screen_finalize()

    def draw_exception(self, exception):
        """Draw exception and wait for keypress.
        :exception: exits the program if user presses 'Q'
        """
        curses.beep()
        message = str(exception) + " Press any key to continue"
        self.screen.addstr(self.height, 0, message, self.color_exception)
        try:
            self.screen.nodelay(False)
            ch = self.screen.getch()
            if ch != -1 and chr(ch) == 'q':
                exit()
        finally:
            self.screen.addstr(self.height, 0, message, self.color_clear)

    def complete(self):
        """Show complete message and wait for keypress. """
        self.screen.addstr(self.height, 0,
                           "Program Complete! Press any key to exit",
                           self.color_complete)
        self.screen.getch()

    def pause(self):
        """Wait for keypress. """
        self.draw_exception("PAUSED")

    def __del__(self):
        """Show complete message and close screen on program end. """
        if self.board_fits():
            self.complete()
            curses.endwin()
