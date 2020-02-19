""" Karel the Robot representation.

Start Karel program with `from karel_robot.run import *` instead.
For more details see README.
"""


class RobotError(Exception):
    """Wrong execution of Karel program - e.g. hitting a Wall. """


class Karel:
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
        """True if Karel is facing in the north direction. """
        return self.facing == self.DIRECTIONS['^']

    def facing_south(self):
        """True if Karel is facing in the south direction. """
        return self.facing == self.DIRECTIONS['v']

    def facing_east(self):
        """True if Karel is facing in the east direction. """
        return self.facing == self.DIRECTIONS['>']

    def facing_west(self):
        """True if Karel is facing in the west direction. """
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
