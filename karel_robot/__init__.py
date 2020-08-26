r""" This file is part of karel_robot package.

Karel Robot
===========

This package provides the classes for robot Karel and his map
of tiles, walls and beepers.

  - This does not import inner packages!

Importing this package does not start the screen and is meant
for testing and code reuse by anyone interested.

If you just want to write Karel programs, start with::

 from karel.run import *

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
from .robot import Karel, Point, RobotError
from .tiles import Tile, Empty, Beeper, Wall, Treasure
from .board import KarelMap, Board, BoardView, MapType
from .window import Window, WindowOpen, screen, KeyHandle, KeysHandler

__all__ = [
    "Karel",
    "Tile",
    "Empty",
    "Wall",
    "Beeper",
    "Treasure",
    "MapType",
    "KarelMap",
    "Board",
    "BoardView",
    "Window",
    "WindowOpen",
    "screen",
    "RobotError",
    "Point",
    "KeyHandle",
    "KeysHandler",
]
