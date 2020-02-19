""" Karel World and its Tiles.

Start Karel program with `from karel_robot.run import *` instead.
For more details see README.
"""
from .robot import *


class Tile:
    """A tile in Karel's world map, by default non-blocking, empty.

    Check for respective children classes with `isinstance`.
    """
    CHARS = "." + Karel.CHARS
    blocking = False

    def __str__(self): return '.'


class Wall(Tile):
    """A Tile that blocks Karel from passing. """
    CHARS = "#"
    blocking = True

    def __str__(self): return '#'


class Beeper(Tile):
    """A Tile from which Karel can `pick_beeper`. """
    CHARS = "123456789"  # 0 is not included <- b = 10k + 0

    def __init__(self, tile=1): self.count = int(tile)

    def __str__(self): return str(self.count % 10)


class Treasure(Tile):
    """A Tile with treasure chest Karel can not pass through. """
    CHARS = "$"
    blocking = True

    def __str__(self): return '$'


def parse_map(map_path):
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


class World:
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
    def karel_tile(self, tile):
        """Set the Tile that Karel is standing on. """
        self.map[self.karel.position[1]][self.karel.position[0]] = tile

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
        return self

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
        return self

    def put_beeper(self):
        """Karel puts down a beeper (if he has any). """
        self.karel.put_beeper()
        if isinstance(self.karel_tile, Beeper):
            self.karel_tile.count += 1
        else:
            self.karel_tile = Beeper()
        return self

    def front_is_blocked(self):
        """True iff Karel can't move forward. """
        return self.karel_facing().blocking

    def front_is_treasure(self):
        """True iff Karel stands in front of a Treasure. """
        return isinstance(self.karel_facing(), Treasure)

    def beeper_is_present(self):
        """True iff Karel stands on a beeper. """
        return isinstance(self.karel_tile, Beeper)
