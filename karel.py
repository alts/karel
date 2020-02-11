""" Karel implementation in python.

Start Karel program with `from karel_run import *` instead.
For more details see README.
"""
import curses
import time

def karel_help():
    print("Karel expected usage:")
    print("python3 YOUR_PROGRAM.py YOUR_WORLD.karelmap")

class RobotError(Exception):
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
        self.position = (
            self.position[0] + self.facing[0],
            self.position[1] + self.facing[1]
        )

    def turn_left(self):
        self.facing = (self.facing[1], -self.facing[0])

    def turn_right(self):
        self.facing = (-self.facing[1], self.facing[0])

    def holding_beepers(self):
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
        if self.beepers is not None:
            self.beepers += 1

    def put_beeper(self):
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

    def __init__(self):
        self.blocking = False

    def __str__(self):
        return '.'


class Wall(Tile):
    CHARS = "#"

    def __init__(self):
        super().__init__()
        self.blocking = True

    def __str__(self):
        return '#'


class Beeper(Tile):
    CHARS = "0123456789"

    def __init__(self, tile=1):
        super().__init__()
        self.count = int(tile)

    def __str__(self):
        return str(self.count % 10)


class Treasure(Tile):
    CHARS = "$"

    def __init__(self):
        super().__init__()
        self.blocking = True

    def __str__(self):
        return '$'


def construct_map(map_path):
    """ Take a filepath to map file and make a robot and a map.

    :param map_path: path to map file, e.g. `levels/00_window.karelmap`
    :return: pair of Karel and map (2D array of int/None)
    """
    karel = None
    karel_map = []
    with open(map_path, 'rb') as f:
        for y, line in enumerate(f):
            row = []
            for x, char in enumerate(line.strip()):
                char = chr(char)  # enumerate str -> [(int, int)]
                if char in Karel.CHARS:
                    karel = Karel((x, y), Karel.DIRECTIONS[char])
                for t in [Tile, Wall, Beeper, Treasure]:
                    if char in t.CHARS:
                        row.append(t(char) if t is Beeper else t())
                        break
            karel_map.append(row)

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

    MAX_SPEED = 100.0

    def __init__(self, map_path, speed=50):
        self.karel, self.map = construct_map(map_path)
        self.speed = self.valid_speed(speed)
        self.screen = None
        # all colors are set in start screen
        self.color_wall = None
        self.color_karel = None
        self.color_beeper = None
        self.color_karel_beeper = None
        self.color_exception = None
        self.color_clear = None
        self.color_complete = None
        self.color_empty = None
        self.start_screen()
        self.draw()

    @property
    def width(self):
        return len(self.map[0])

    @property
    def height(self):
        return len(self.map)

    @property
    def karel_tile(self):
        """ The tile that Karel is standing on.

        :return: always int, as Karel is not in wall
        """
        return self.map[self.karel.position[1]][self.karel.position[0]]

    @karel_tile.setter
    def karel_tile(self, t):
        self.map[self.karel.position[1]][self.karel.position[0]] = t

    def karel_facing(self):
        x = self.karel.position[0] + self.karel.facing[0]
        y = self.karel.position[1] + self.karel.facing[1]
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return Wall()
        return self.map[y][x]

    def valid_speed(self, speed):
        if speed < 0:
            return 0
        elif speed > self.MAX_SPEED:
            return self.MAX_SPEED
        else:
            return speed

    def start_screen(self):
        self.screen = curses.initscr()
        my, mx = self.screen.getmaxyx()
        if my < self.height or mx < self.width:
            raise RuntimeError("Window not big enough ({}, {}) / "
                               "World too big ({}, {})"
                               .format(mx, my, self.width, self.height))
        curses.start_color()
        # Wall
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
        self.color_wall = curses.color_pair(1)
        # Karel
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        self.color_karel = curses.color_pair(2)
        # Beeper
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.color_beeper = curses.color_pair(3)
        # Karel on beeper
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        self.color_karel_beeper = curses.color_pair(4)
        # Exception First
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        self.color_exception = curses.color_pair(5)
        # Exception Second
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLACK)
        self.color_clear = curses.color_pair(6)
        # Complete Message
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.color_complete = curses.color_pair(7)
        # Empty tile
        curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.color_empty = curses.color_pair(8)

    def wait(self):
        time.sleep((self.MAX_SPEED - self.speed) / self.MAX_SPEED)

    def draw_tile(self, x, y, tile):
        if isinstance(tile, Wall):
            color = self.color_wall
        elif isinstance(tile, Beeper) or isinstance(tile, Treasure):
            color = self.color_beeper
        else:
            color = self.color_empty
        self.screen.addstr(y, x, str(tile), color)

    def draw_karel_tile(self, moved=False):
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
        self.screen.addstr(self.height + 1, 0, ' ')
        self.screen.refresh()
        # quit if user presses 'q'
        self.screen.nodelay(True)
        self.wait()
        ch = self.screen.getch()
        self.screen.nodelay(False)
        if ch != -1 and chr(ch) == 'q':
            exit(1)
        if ch != -1 and chr(ch) == 'p':
            self.pause()

    def draw(self):
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                self.draw_tile(x, y, tile)
        self.draw_karel_tile()
        self.screen_finalize()

    def redraw(self, moved=False):
        self.draw_karel_tile(moved)
        self.screen_finalize()

    def draw_exception(self, exception):
        curses.beep()
        message = str(exception) + " Press any key to continue"
        self.screen.addstr(self.height, 0, message, self.color_exception)
        ch = self.screen.getch()
        if chr(ch) == 'q':
            exit(1)
        self.screen.addstr(self.height, 0, message, self.color_clear)

    def complete(self):
        self.screen.addstr(self.height, 0,
                           "Program Complete! Press any key to exit",
                           self.color_complete)
        self.screen.getch()

    def pause(self):
        self.draw_exception("PAUSED")

    def move(self):
        if self.front_is_blocked():
            raise RobotError("Can't move. Karel is blocked!")
        self.karel.move()

    def pick_beeper(self):
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
        self.karel.put_beeper()
        if isinstance(self.karel_tile, Beeper):
            self.karel_tile.count += 1
        else:
            self.karel_tile = Beeper()

    def front_is_blocked(self):
        return self.karel_facing().blocking

    def front_is_treasure(self):
        return isinstance(self.karel_facing(), Treasure)

    def beeper_is_present(self):
        return isinstance(self.karel_tile, Beeper)

    def __del__(self):
        self.complete()
        curses.endwin()
