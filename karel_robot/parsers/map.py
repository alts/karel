""" Parse Karel map file.

Example simple map, with tiles and Karel represented by one character::

    ..>.1
    ....#

For more then 9 beepers or beepers under Karel, use header and spaces::

    KAREL 2 1 > 0
    .  .  .  .  .  #
    $  #  5  . 12  .

This will put Karel right on the ``5`` beepers and make him start with no
beepers in his bag (``0``). To make his beeper bag unlimited use ``N``.

==============================================================================
                                   LICENSE
==============================================================================

The karel_robot package is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

The karel_robot package is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
the karel_robot package. If not, see `<https://www.gnu.org/licenses/>`_.
"""
from typing import Tuple, Dict, Iterable, Optional
from .. import Karel, RobotError, Point, Tile, Empty, Wall, Beeper, Treasure


class MapParser:
    """ Take lines/map file and make a robot and a map.

    Attributes:
        karel: the robot to override map
        karel_map: mapping of (x,y) to tiles, leaving out Empty
        height: of the map
        width: of the map
    """

    def __init__(
        self,
        lines: Iterable[str],
        karel: Optional[Karel] = None,
        new_style_map: bool = False,
    ):
        """ Take lines/map file and make a robot and a map.

        Args:
            lines: of the map, e.g. open file or ['>.', '.1']
            karel: use this karel instead (better warning)
            new_style_map: if tiles are separated by spaces and has header
        Raises:
            RobotError: on incorrect map or if Karel is not present
        """
        self.karel: Optional[Karel] = karel  # docstring below
        self._karel_override = karel is None

        self.karel_map: Dict[Tuple[int, int], Tile] = dict()
        """ Mapping of (x,y) to tiles, leaving out Empty """
        self.width: Optional[int] = None
        """ Width of the map, with None meaning no limit """
        self.height: Optional[int] = None
        """ Height of the map, with None meaning no limit """

        self._empty = Empty()
        self._wall = Wall()
        self._lines = iter(lines)
        self._lineno = lambda y: y + new_style_map + 1
        if new_style_map:
            try:
                header = next(self._lines)
            except StopIteration:
                raise RobotError("line 0: Map empty!")
            if karel is None:
                self.karel = self.parse_new_map_header(header)
                """ The robot, basically (position * direction) """
        self._parse(new_style_map)

    def _parse(self, new_style_map: bool):
        """ Parse map into self map, width and height variables. """
        y = None
        for y, line in enumerate(self._lines):
            self._parse_line(y, line, new_style_map)
        if y is None:
            raise RobotError("Map is empty!")
        self.height = y + 1
        if self.karel is None:
            raise RobotError("Karel must be placed on the map!")

    def _parse_line(self, y: int, line: str, new_style_map: bool):
        """ Parse one line of map, splitting characters or on space if new-style."""
        tokens = line.split() if new_style_map else line.strip()

        if not tokens or self.width is not None and self.width != len(tokens):
            raise ValueError(
                f"line {self._lineno(y)}: " "Karel map must be a rectangle!"
            )
        self.width = len(tokens)

        x = None
        for x, char in enumerate(tokens):
            t = self._parse_tile(char, x, y)
            if t is not None and t is not self._empty:
                self.karel_map[x, y] = t
        if x is None:
            raise RobotError(f"line {self._lineno(y)}: Is Empty!")

    @staticmethod
    def parse_new_map_header(line: str) -> Karel:
        """ Parse the first line of map, that sets Karel.

        Raises:
            RobotError: on line not matching the form 'KAREL X Y > B', where
                        X,Y are coordinates, > is one of the directions
                        and B is number of beepers or 'N' for infinite
        """
        try:
            k, kx, ky, kd, kb = line.split()
            if k[0].lower() != "k":
                raise RobotError(f"Karel not set ({k} != KAREL)")
            if kd not in Karel.CHARS:
                raise ValueError()
            return Karel(
                position=Point(x=int(kx), y=int(ky)),
                facing=kd,
                beepers=int(kb) if kb != "N" else None,
            )
        except ValueError:
            raise RobotError("Map header not in form 'KAREL X Y > B'")

    def _parse_tile(self, token: str, x: int, y: int) -> Optional[Tile]:
        """ Parse one token, e.g. ``'.'`` or ``'#'`` or ``'1984'``.

        Raises:
            RobotError: on token that does not make valid Tile, e.g. '1Q94'.
        """
        if token in Karel.CHARS:
            if self.karel is None:
                self.karel = Karel(Point(x, y), token)
            elif not self._karel_override and self.karel is not None:
                raise RobotError(f"Karel is already on {self.karel.position}.")
            return None
        for tile in self._empty, self._wall, Treasure():
            if token in tile.chars:
                return tile
        try:
            if int(token) > 0:
                return Beeper(count=int(token))
        except ValueError:
            pass
        raise RobotError(
            f"line {self._lineno(y)}: Invalid token '{token}' in column {x+1}."
        )
