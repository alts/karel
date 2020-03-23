r""" This file is part of karel_robot package.

Karel World Tiles
==================

This file defines the pure class :class:`Tile` and its children:
  - :class:`Tile` through which Karel can pass freely
  - :class:`Wall` which blocks Karel
  - :class:`Beeper`, a tile with beepers for Karel to pick up

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
from dataclasses import dataclass
from typing import Optional, TypeVar, Type


@dataclass
class Tile:
    """ A tile in Karel's world map, by itself non-blocking, empty.

    Check for children classes with isinstance.
    """

    chars: str
    """ Character(s) representing the Tile in map. Also used when parsing. """
    blocking: bool
    """ Whether :class:`karel_robot.robot.Karel` can pass through the Tile. """

    def __str__(self):
        """ The character to be printed on screen.

        WARNING: overwrite if ``len(chars) > 1``.
        """
        return self.chars


AnyTile = TypeVar("AnyTile", bound=Tile)


@dataclass
class Empty(Tile):
    """ Wall to block Karel from passing. """

    chars: str = ".0"
    blocking: bool = False

    def __str__(self):
        return '.'

    def __repr__(self):
        return "Empty()"


@dataclass
class Wall(Tile):
    """ Wall to block Karel from passing. """

    chars: str = "#"
    blocking: bool = True

    def __repr__(self):
        return "Wall()"


@dataclass
class Treasure(Tile):
    """ Treasure chest that Karel can not pass through. """

    chars: str = "$"
    blocking: bool = True

    def __repr__(self):
        return "Treasure()"


@dataclass
class Beeper(Tile):
    """ A Tile from which Karel can `pick_beeper`. """

    count: int = 1
    chars: str = "123456789"  # 0 is not included <- b = 10k + 0
    blocking: bool = False

    def __str__(self):
        return str(self.count) if self.count <= 9 else "+"

    def __repr__(self):
        return f"Beeper({self.count})"


def _one_tile(cls: Type[Tile], set_share: Optional[bool] = None) -> Optional[AnyTile]:
    """ One **shared default instance** of class, same between calls.

    Args:
        cls: Tile class to get one shared instance.
        set_share: if False, then calls with this class return None.

    Returns:
        The instance of the class cls or None if set_share was False.
    """
    if type(set_share) is bool:
        cls._share_one_tile = set_share
    if hasattr(cls, "_share_one_tile") and not cls._share_one_tile:
        return
    if set_share or not hasattr(cls, "_the_one"):
        cls._the_one = cls()
    return cls._the_one


def one_tile_set(cls: Type[Tile], set_share: bool = True) -> None:
    """ Set if this Tile class should have a one shared instance. """
    _one_tile(cls, set_share)


def one_tile(cls: Type[Tile]) -> AnyTile:
    """ Get one shared instance of class.

    Raises:
        ValueError: if class was set to not share one Tile.
    """
    i = _one_tile(cls)
    if i is None:
        raise ValueError(f"Class {cls.__name__} was set not to share one tile.")
    return i


one_tile_set(Tile, set_share=False)
one_tile_set(Empty)
one_tile_set(Wall)
one_tile_set(Treasure)
one_tile_set(Beeper, set_share=False)
