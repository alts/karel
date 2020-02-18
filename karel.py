""" Karel implementation in python.

Start Karel program with `from karel_run import *` instead.
For more details see README.
"""
import curses
import time

class RobotError(Exception):
    """Wrong execution of Karel program - e.g. hitting a Wall. """
    pass

###########################################################
#                      THE ROBOT CLASS                    #
###########################################################

class Karel(object):
    """ Karel the Robot.

    Karel is a shortsighted robot, that carries around
    and picks up beepers (possibly infinitely many) on
    a 2D grid.
    """
    DIRECTIONS = {
        '>': (1, 0),
        '^': (0, -1),
        '<': (-1, 0),
        'v': (0, 1),
    }
    CHARS = ''.join(list(DIRECTIONS))
    INV_DIR = {v: k for k, v in DIRECTIONS.items()}

    def __init__(self, position, facing=DIRECTIONS['^'], beepers=None):
        self.position = position  # (x,y) where y is row number
        self.facing = facing  # see DIRECTIONS
        self.beepers = beepers  # if None then Karel has infinite beepers

    def to_dir(self):
        """Print Karel on board as one of '>^<v'. """
        return Karel.INV_DIR[self.facing]

    def move(self):
        """"Karel moves in the direction that he is facing. """
        self.position = (
            self.position[0] + self.facing[0],
            self.position[1] + self.facing[1]
        )

    def turn_left(self):
        """Karel turns 90° anti-clockwise. """
        self.facing = (self.facing[1], -self.facing[0])

    def turn_right(self):
        """Karel turns 90° clockwise. """
        self.facing = (-self.facing[1], self.facing[0])

    def holding_beepers(self):
        """True if Karel has some or unlimited beepers. """
        return self.beepers is None or self.beepers > 0

    def facing_north(self):
        return self.facing == self.DIRECTIONS['^']

    def facing_south(self):
        return self.facing == self.DIRECTIONS['v']

    def facing_east(self):
        return self.facing == self.DIRECTIONS['>']

    def facing_west(self):
        return self.facing == self.DIRECTIONS['<']

    def pick_beeper(self):
        """Increase beeper count if it is limited. """
        if self.beepers is not None:
            self.beepers += 1

    def put_beeper(self):
        """Decrease beeper count if it is limited.
        :raises: RobotError on 0 beepers
        """
        if not self.holding_beepers():
            raise RobotError("Can't put beeper. Karel has none!")
        if self.beepers is not None:
            self.beepers -= 1


###########################################################
#                       KAREL WORLD                       #
###########################################################

class Tile(object):
    """A tile in Karel's world map, by default non-blocking, empty.

    Check for respective children classes with isinstance.
    """
    CHARS = "." + Karel.CHARS
    blocking = False
    def __str__(self): return '.'


class Wall(Tile):
    CHARS = "#"
    blocking = True
    def __str__(self): return '#'


class Beeper(Tile):
    CHARS = "0123456789"
    def __init__(self, tile=1): self.count = int(tile)
    def __str__(self): return str(self.count % 10)


class Treasure(Tile):
    CHARS = "$"
    blocking = True
    def __str__(self): return '$'


def construct_map(map_path):
    """ Take a filepath to map file and make a robot and a map.

    :param map_path: path to map file, e.g. `levels/00_window.karelmap`
    :raises: RuntimeError on incorrect map
    :return: pair of Karel and map - (Karel, [[Tile]])
    """
    karel = None

    def parse_tile(c, x, y):
        nonlocal karel  # better then reading twice
        if c in Karel.CHARS:
            if karel is not None:
                raise RuntimeError("Multiple Karel robots are not supported.")
            karel = Karel((x, y), Karel.DIRECTIONS[c])
        for t in [Tile, Wall, Beeper, Treasure]:
            if c in t.CHARS:
                return t(c) if t is Beeper else t()
        raise RuntimeError("The character: '{}' in {} on line {} column {} is invalid."
                           .format(c, y, x, map_path))

    with open(map_path, 'rb') as f:
        karel_map = [[parse_tile(chr(char), x, y)
                      for x, char in enumerate(line.strip())]
                     for y, line in enumerate(f)]

    if karel is None:
        raise RuntimeError("Karel must be present on the map!")

    if any(len(x) != len(karel_map[0]) for x in karel_map):
        raise RuntimeError("Karel map must be a rectangle!")

    return karel, karel_map


class Board(object):
    """
    Example map of Karel world:
    1..#...
    #....^.

    Legend:
    - one beeper ('1') is on (0,0)
    - robot Karel ('^') is on (5,1)
    - two walls on (3,0) and (0,1)
    """

    def __init__(self, karel, karel_map):
        self.karel = karel
        self.map = karel_map

    @property
    def width(self):
        """The width of the map. """
        return len(self.map[0])

    @property
    def height(self):
        """The height of the map. """
        return len(self.map)

    @property
    def karel_tile(self):
        """Get the Tile that Karel is standing on. """
        return self.map[self.karel.position[1]][self.karel.position[0]]

    @karel_tile.setter
    def karel_tile(self, t):
        """Set the Tile that Karel is standing on. """
        self.map[self.karel.position[1]][self.karel.position[0]] = t

    def karel_facing(self):
        """The Tile that Karel is facing or Wall iff end of the world. """
        x = self.karel.position[0] + self.karel.facing[0]
        y = self.karel.position[1] + self.karel.facing[1]
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return Wall()
        return self.map[y][x]

    def move(self):
        """Karel tries to move in the direction he is facing. """
        if self.front_is_blocked():
            raise RobotError("Can't move. Karel is blocked!")
        self.karel.move()

    def pick_beeper(self):
        """Karel tries to pick up a beeper. """
        tile = self.karel_tile
        if isinstance(tile, Beeper):
            if tile.count > 1:
                self.karel_tile.count -= 1
            else:
                self.karel_tile = Tile()
            self.karel.pick_beeper()
        else:
            raise RobotError("Can't pick beeper from empty location")

    def put_beeper(self):
        """Karel puts down a beeper (if he has any). """
        self.karel.put_beeper()
        if isinstance(self.karel_tile, Beeper):
            self.karel_tile.count += 1
        else:
            self.karel_tile = Beeper()

    def front_is_blocked(self):
        """True iff Karel can't move forward. """
        return self.karel_facing().blocking

    def front_is_treasure(self):
        """True iff Karel stands in front of a Treasure. """
        return isinstance(self.karel_facing(), Treasure)

    def beeper_is_present(self):
        """True iff Karel stands on a beeper. """
        return isinstance(self.karel_tile, Beeper)


###########################################################
#                   CURSED TEXT WINDOW                    #
###########################################################

class Window(Board):
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
        my, mx = self.screen.getmaxyx()
        fits = my > self.height and mx >= self.width
        if not fits and throw:
            raise RobotError("Window too small ({}, {}) and World too big ({}, {} + 1)"
                             .format(mx, my, self.width, self.height))
        return fits

    def valid_speed(self, speed):
        """Return the speed in `(0, MAX_SPEED)` or either end. """
        if speed < 0:
            return 0
        elif speed > self.MAX_SPEED:
            return self.MAX_SPEED
        else:
            return speed

    def wait(self):
        """Wait for `(m-x)/m` seconds. """
        time.sleep((self.MAX_SPEED - self.speed) / self.MAX_SPEED)

    def draw_tile(self, column, row, tile):
        """Draw the tile on (column, row). """
        if isinstance(tile, Wall):
            color = self.color_wall
        elif isinstance(tile, Beeper) or isinstance(tile, Treasure):
            color = self.color_beeper
        else:
            color = self.color_empty
        self.screen.addstr(row, column, str(tile), color)

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

    def draw(self):
        """Draw the whole board. """
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                self.draw_tile(x, y, tile)
        self.draw_karel_tile()
        self.screen_finalize()

    def redraw(self, moved=False):
        """Redraw Karel's tile and the one he `moved` from."""
        self.draw_karel_tile(moved)
        self.screen_finalize()

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
