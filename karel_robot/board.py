r""" This file is part of karel_robot package.

Karel's Board
=============

This file defines the pure class :class:`KarelMap` and its children:
  - :class:`KarelMap` that stores and accesses the tiles
  - :class:`Board` focuses on tiles around Karel
  - :class:`BoardView` models a limited view on the map

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
from typing import MutableMapping, Tuple, Optional
from .robot import Karel, KAREL_DIR, Point, RobotError
from .tiles import Tile, Empty, Beeper, Wall, Treasure

MapType = MutableMapping[Tuple[int, int], Tile]
""" Type whose instance ``m`` support ``m[x,y]``. """


class KarelMap:
    """ Container for tiles on a square grid.

    Example map of Karel world::

      1..#...
      #....^.

    Legend:
      - multiple :class:`Empty` tiles (``.``)

      - one :class:`Beeper` (``1``) is on (0,0)

      - robot :class:`Karel` (``^``) is on (5,1) and on plain map
        his starting tile is :class:`Empty`

      - blocking :class:`Wall` (``#``) on (3,0) and on (0,1)

        - space outside of view is also considered to be :class:`Wall`

    A map is infinite by default and can also be infinite in one dimension only::

        >.1...11..111.1.1.11...11.11.1.11.1.11..1.11.1111.111.1.1

    Note that y-coordinate is flipped to ease parsing and printing to screen.
    """

    def __init__(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        tiles: Optional[MapType] = None,
    ):
        """ Setup by default infinite map of Karel's world.

        Args:
            x: The width of the map.
            y: The height of the map.
            tiles: Mutable map supporting tiles[x, y].
        """
        self.x: Optional[int] = x
        """ The x_view of the map. """
        self.y: Optional[int] = y
        """ The y_view of the map. """
        self._tiles: MapType = dict() if tiles is None else tiles
        """ Mutable map supporting ``_tiles[x,y]``. """

    def in_range(self, x: int, y: int):
        """ Check if map is unlimited or includes this coordinate. """

        def in_range(i, top):
            return top is None or 0 <= i < top

        return in_range(y, self.y) and in_range(x, self.x)

    def __getitem__(self, xy: Tuple[int, int]) -> Tile:
        """ Access tile at coordinate.

        If tiles have border (0, 0 to x_map, y_map) then accessing tiles
        beyond it returns :class:`Wall`. If tiles are unbounded, then
        coordinates not contained them it return :class:`Empty`.
        """
        if not self.in_range(*xy):
            return Wall()
        return self._tiles.get(xy, Empty())

    def __setitem__(self, xy: Tuple[int, int], tile: Tile) -> None:
        """ Set tile at coordinate. """
        if isinstance(tile, Empty) and xy in self._tiles:
            del self._tiles[xy]
        elif self.in_range(*xy):
            self._tiles[xy] = tile

    def __len__(self):
        """ Number of tiles. """
        if self.x is None or self.y is None:
            raise ValueError("This KarelMap is unbounded")
        return self.x * self.y

    def __bool__(self):
        """ Check if nonempty. """
        return self.x is None or self.y is None or len(self)

    def min_coordinate(self, default=Point(0, 0)) -> Point:
        """ Minimal coordinate of the map. """
        points = self._tiles.keys() | {default}
        return Point(
            x=min(map(lambda p: p[0], points)), y=min(map(lambda p: p[1], points)),
        )

    def max_coordinate(self, default=Point(0, 0)) -> Point:
        """ Maximal coordinate of the map. """
        points = self._tiles.keys() | {default}
        return Point(
            x=max(map(lambda p: p[0], points)), y=max(map(lambda p: p[1], points)),
        )


class Board:
    """ Manage :class:`Karel` on a board.
    """

    def __init__(
        self,
        karel: Optional[Karel] = None,
        x_map: Optional[int] = None,
        y_map: Optional[int] = None,
        tiles: Optional[MapType] = None,
    ):
        """ Setup by default infinite board with Karel the robot.

        Args:
            karel: The robot or default Karel if None.
            x_map: The width of the map.
            y_map: The height of the map.
            tiles: Mutable map supporting tiles[y][x], like list or dict
                   (if dict then indices not in tiles are considered Empty).

        Description copied from :class:`KarelMap`.
        """
        self.karel_map = KarelMap(x_map, y_map, tiles)
        self.karel = karel or Karel()
        """ The robot living on the board. """
        if self.karel_map[self.karel.position].blocking:
            raise RobotError("Karel can not move!")

    @property
    def karel_tile(self) -> Tile:
        """ The :class:`Tile` that :class:`Karel` is standing on. """
        return self.karel_map[self.karel.position]

    @karel_tile.setter
    def karel_tile(self, tile: Tile):
        self.karel_map[self.karel.position] = tile

    @property
    def karel_facing(self) -> Tile:
        """ The :class:`Tile` that :class:`Karel` is facing.
        Iff beyond board, then :class:`Wall`.
        """
        x = self.karel.position.x + self.karel.facing.x
        y = self.karel.position.y + self.karel.facing.y
        return self.karel_map[x, y]

    @karel_facing.setter
    def karel_facing(self, tile: Tile):
        """ The :class:`Tile` that :class:`Karel` is facing.
        If beyond board, then ignored.
        """
        x = self.karel.position.x + self.karel.facing.x
        y = self.karel.position.y + self.karel.facing.y
        self.karel_map[x, y] = tile

    def move(self):
        """Karel tries to move in the direction he is facing. """
        if self.front_is_blocked():
            raise RobotError("Can't move. Karel is blocked!")
        self.karel.move()
        return self

    def pick_beeper(self) -> Board:
        """ :class:`Karel` tries to pick up a :class:`Beeper`. """
        tile = self.karel_tile
        if isinstance(tile, Beeper):
            if tile.count > 1:
                tile.count -= 1
            else:
                self.karel_tile = Empty()
            self.karel.pick_beeper()
        else:
            raise RobotError(f"Can't pick Beeper from {repr(self.karel_tile)}")
        return self

    def put_beeper(self) -> Board:
        """ :class:`Karel` puts down a :class:`Beeper` (if he has any). """
        self.karel.put_beeper()
        tile = self.karel_tile
        if isinstance(tile, Beeper):
            tile.count += 1
        else:
            self.karel_tile = Beeper()
        return self

    def front_is_blocked(self) -> bool:
        """ True iff :class:`Karel` can't move forward. """
        return self.karel_facing.blocking

    def front_is_treasure(self) -> bool:
        """ True iff :class:`Karel` stands in front of a :class:`Treasure`. """
        return isinstance(self.karel_facing, Treasure)

    def beeper_is_present(self) -> bool:
        """ True iff :class:`Karel` stands on a :class:`Beeper`. """
        return isinstance(self.karel_tile, Beeper)


class BoardView(Board):
    """ Board with limited view, that shifts with :class:`Karel`.
    """

    def __init__(
        self,
        x_view: int,
        y_view: int,
        lookahead: int = 1,
        karel=None,
        x_map=None,
        y_map=None,
        tiles=None,
    ):
        """ Setup by default infinite board viewed through limited
        window, that shifts with :class:`Karel`.

        Args:
            x_view: The x-axis size of the window.
            y_view: The y-axis size of the window.
            lookahead: The number of fields visible ahead of Karel.
            karel: The robot or default Karel if None.
            x_map: The width of the map.
            y_map: The height of the map.
            tiles: Mutable map supporting tiles[y][x], like list or dict
                   (if dict then indices not in tiles are considered Empty).

        Description copied from :class:`Board` and :class:`KarelMap`.
        """
        super().__init__(karel, x_map, y_map, tiles)
        self.x_view = x_view
        """ The x_view of the view on Karel's world. """
        self.y_view = y_view
        """ The y_view of the view on Karel's world. """
        self.advanced = False
        """ Use to check if last call to move advanced the view. """
        self._lookahead: int = max(0, lookahead)
        """ The number of fields visible ahead of Karel """
        self.offset: Point = Point(0, 0)
        """ Top left tile position in the real map coordinates. """
        self.reset_offset()

    def reset_offset(self):
        """ Recalculate the top-left corner iff necessary. """

        def offset(pos_karel, abs_max, rel_max):
            """  Calculate offset for one dimension.
            Args:
                pos_karel: Karel's position
                abs_max: The size of the map if any
                rel_max: The size of the screen
            """
            if abs_max is None:  # shift the border only
                # m checks for case of 1 line view
                m = min(rel_max - 1, self._lookahead)
                if pos_karel > rel_max:
                    return pos_karel - rel_max + 1 + m
                elif pos_karel < m:
                    return pos_karel - m
                else:
                    return 0
            return max(0, min(pos_karel, abs_max - rel_max))

        x_ok = 0 < self.karel_pos.x < self.x_view
        y_ok = 0 < self.karel_pos.y < self.y_view
        offset_new = Point(
            x=offset(self.karel.position.x, self.karel_map.x, self.x_view),
            y=offset(self.karel.position.y, self.karel_map.y, self.y_view),
        )
        self.offset = Point(
            x=self.offset.x if x_ok else offset_new.x,
            y=self.offset.y if y_ok else offset_new.y,
        )

    @property
    def karel_pos(self) -> Point:
        """ Karel's position in the shifted coordinates. """
        xk, yk = self.karel.position
        x, y = self.offset
        return Point(x=xk - x, y=yk - y)

    def border_visible(self, direction: Optional[KAREL_DIR] = None) -> bool:
        """ Check if border is in view. """
        if direction is None:
            direction = self.karel.to_dir()
        if direction == "<":
            return self.karel_map.x is not None and self.offset.x == 0
        if direction == ">":
            return self.karel_map.x == self.offset.x + self.x_view
        if direction == "^":
            return self.karel_map.y is not None and self.offset.y == 0
        if direction == "v":
            return self.karel_map.y == self.offset.y + self.y_view

    def karel_lookahead(self) -> bool:
        """ Check if there if karel can advance the view ahead. """
        x, y = self.karel_pos
        direction = self.karel.to_dir()
        if direction == "<":
            return x <= self._lookahead
        if direction == ">":
            return x >= self.x_view - self._lookahead - 1
        if direction == "^":
            return y <= self._lookahead
        if direction == "v":
            return y >= self.y_view - self._lookahead - 1

    def move(self) -> BoardView:
        """ Move view in along with :class:`Karel`. """
        self.advanced = not self.border_visible() and self.karel_lookahead()
        if self.advanced:
            self.offset = Point(
                x=self.offset.x + self.karel.facing.x,
                y=self.offset.y + self.karel.facing.y,
            )
        super(BoardView, self).move()
        return self

    def get_pos(self, x, y) -> Point:
        """ Translate from relative (view) position to absolute (map).

        This also works for **one tile** beyond boundary.
        """
        if -1 <= x <= self.x_view and -1 <= y <= self.y_view:
            return Point(x=x + self.offset.x, y=y + self.offset.y)
        raise RuntimeError("BoardView accessed beyond the boundary. ")

    def get_view(self, x, y) -> Tile:
        """ Access tile at shifted (view) coordinate. """
        return self.karel_map[self.get_pos(x, y)]

    def set_view(self, x, y, tile):
        """ Set tile at shifted (view) coordinate. """
        self.karel_map[self.get_pos(x, y)] = tile
