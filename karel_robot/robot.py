r""" This file is part of karel_robot package.

Karel the Robot
===============

This file defines the pure class :class:`Karel` to represent
a robot positioned on a square grid/tiled board.

See the README in the package root folder for general take and the
one in this folder for details.

^^^^^^^
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
from typing import NamedTuple, Dict, Union, List, Optional

# wait for 3.8
KAREL_DIR = str  # Literal[">", "<", "^", "v"]


class Point(NamedTuple):
    """ Better way to access 2-vector of ints, otherwise same as tuple. """
    x: int
    y: int


class RobotError(RuntimeError):
    """Wrong execution of Karel program - e.g. hitting a Wall. """


class Karel:
    """ Karel the Robot.

    Karel is a shortsighted robot, that carries around
    and picks up beepers (possibly infinitely many) on
    a 2D grid.
    """

    DIRECTIONS: Dict[KAREL_DIR, Point] = {
        ">": Point(x=1, y=0),
        "^": Point(x=0, y=-1),
        "<": Point(x=-1, y=0),
        "v": Point(x=0, y=1),
    }

    CHARS: List[KAREL_DIR] = list(DIRECTIONS.keys())

    INV_DIR: Dict[Point, KAREL_DIR] = {v: k for k, v in DIRECTIONS.items()}

    def __init__(
        self,
        position: Union[Point, None] = None,
        facing: Union[Point, KAREL_DIR] = ">",
        beepers: int = None,
    ):
        self.position: Point = Point(0, 0) if position is None else Point(*position)
        """ Coordinates of tile that Karel is standing on. """

        if isinstance(facing, Point):
            self.facing: Point = facing
            """ Direction that Karel is facing. """
        elif facing in self.CHARS:
            self.facing = self.DIRECTIONS[facing]
        else:
            raise ValueError(f"Karel can not look in the '{facing}' direction")

        self.beepers: Optional[int] = beepers
        """ Number of beeper Karel can put down (if None then infinite). """

    def __repr__(self):
        return (
            f"Karel({self.position}, {self.to_dir()}"
            f"{'' if self.beepers is None else ', beepers=' + str(self.beepers)}"
            ")"
        )

    def to_dir(self) -> KAREL_DIR:
        """ Karel one character representation showing direction, e.g '>'. """
        return Karel.INV_DIR[self.facing]

    def move(self) -> Karel:
        """"Karel moves in the direction that he is facing. """
        self.position = Point(
            x=self.position.x + self.facing.x, y=self.position.y + self.facing.y
        )
        return self

    def turn_left(self) -> Karel:
        """ Karel turns 90° anti-clockwise. """
        self.facing = Point(self.facing.y, -self.facing.x)
        return self

    def turn_right(self) -> Karel:
        """ Karel turns 90° clockwise. """
        self.facing = Point(-self.facing.y, self.facing.x)
        return self

    def holding_beepers(self) -> bool:
        """ True if Karel has some or unlimited beepers. """
        return self.beepers is None or self.beepers > 0

    def facing_dir(self, direction: KAREL_DIR) -> bool:
        """ True if Karel is facing in the north direction. """
        return self.to_dir() == direction

    def pick_beeper(self) -> Karel:
        """ Increase beeper count if it is limited. """
        if self.beepers is not None:
            self.beepers += 1
        return self

    def put_beeper(self) -> Karel:
        """ Decrease beeper count if it is limited.

        :raises RobotError: on 0 beepers
        """
        if not self.holding_beepers():
            raise RobotError("Can't put beeper. Karel has none!")
        if self.beepers is not None:
            self.beepers -= 1
        return self
