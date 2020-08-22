""" Parse Karel map file, see the MapParser for more details.

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
from typing import Tuple, Dict, Iterable, Optional, Callable, Type
from .. import *
from .. import AnyTile, Tile


class MapParser:
    """ Take lines/map file and make a robot and a map.

    Example simple map, with tiles and Karel represented by one character::

        ..>.1
        ....#

    For more then 9 beepers or beepers under Karel, use header and spaces::

        KAREL 2 1 > 0
        .  .  .  .  .  #
        $  #  5  . 12  .

    This will put Karel right on the ``5`` beepers and make him start with no
    beepers in his bag (``0``). To make his beeper bag unlimited use ``N``.

    Attributes:
        karel: the robot
        karel_map: mapping of (x,y) to tiles, leaving out Empty
        height: of the map
        width: of the map
    """
    def __init__(
        self,
        lines: Iterable[str],
        sharing: bool = True,
        karel: Optional[Karel] = None,
        new_style_map: bool = False,
    ):
        """ Take lines/map file and make a robot and a map.

        Args:
            lines: of the map, e.g. open file or ['>.', '.1']
            sharing: uses a shared constants for tiles (except Beeper)
            karel: use this karel instead (better warning)
            new_style_map: space separated tiles and specified Karel and dimensions.
        Raises:
            RobotError: on incorrect map or if Karel is not present
        """
        self.karel: Karel = karel
        self.karel_map: Dict[Tuple[int, int], AnyTile] = dict()
        self.width = None
        self.height = None

        self._karel_is_set: bool = karel is not None
        self._make_tile: Callable[[Type[Tile]], AnyTile] = one_tile if sharing else lambda cls: cls()
        self._lines = iter(lines)
        self._skip_tokens = Empty.chars
        self._new_style = new_style_map
        self._lineno = lambda y: y + self._new_style + 1
        if self._new_style:
            try:
                header = next(self._lines)
            except StopIteration:
                raise RobotError("line 0: Map empty!")
            if not self._karel_is_set:
                self.karel = self.parse_new_map_header(header)
        self._parse()

    def _parse(self):
        y = None
        for y, line in enumerate(self._lines):
            self._parse_line(y, line)

        if y is None:
            raise RobotError("Map is empty!")
        self.height = y + 1
        if self.karel is None:
            raise RobotError("Karel must be placed on the map!")

    def _parse_line(self, y: int, line: str):
        """ Parse one line of map, splitting characters or on space if new-style."""
        tokens = line.split() if self._new_style else line.strip()

        if not tokens or self.width is not None and self.width != len(tokens):
            raise ValueError(f"line {self._lineno(y)}: "
                             "Karel map must be a rectangle!")
        self.width = len(tokens)

        x = None
        for x, char in enumerate(tokens):
            t = self._parse_tile(char, x, y)
            if t is not None:
                self.karel_map[x, y] = t
        if x is None:
            raise RobotError(f"line {self._lineno(y)}: Is Empty!")

    @staticmethod
    def parse_new_map_header(line: str, no_error: bool = False) -> Karel:
        """ Parse the first line of map, that sets Karel.

        Raises:
            RobotError: on line not matching the form 'KAREL X Y > B', where
                        X,Y are coordinates, > is one of the directions
                        and B is number of beepers or 'N' for infinite
        """
        try:
            k, kx, ky, kd, kb = line.split()
            if k[0].lower() != "k" and not no_error:
                raise RobotError(f"Karel not set ({k} != KAREL)")
            if kd not in Karel.CHARS:
                raise ValueError()
            return Karel(
                position=Point(x=int(kx), y=int(ky)),
                facing=kd,
                beepers=int(kb) if kb != "N" else None,
            )
        except ValueError:
            if not no_error:
                raise RobotError("Map header not in form 'KAREL X Y > B'")

    def _parse_tile(self, token: str, x: int, y: int) -> Optional[AnyTile]:
        """ Parse one token, e.g. ``'.'`` or ``'#'`` or ``'1984'``.

        Raises:
            RobotError: on token that does not make valid Tile, e.g. '1Q94'.
        """
        if token in Karel.CHARS:
            if self.karel is None:
                self.karel = Karel(Point(x, y), token)
            elif not self._karel_is_set:  # another Karel on map, but allow override
                raise RobotError(f"Karel is already on {self.karel.position}.")
            return
        if token in self._skip_tokens:
            return
        for tile in (Wall, Treasure):
            if token in tile.chars:
                return self._make_tile(tile)
        try:
            if int(token) > 0:
                return Beeper(count=int(token))
        except ValueError:
            pass
        raise RobotError(f"line {self._lineno(y)}: Invalid token '{token}' in column {x+1}.")
