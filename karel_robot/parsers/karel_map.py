from typing import Tuple, Iterable
from ..tiles import *
from ..robot import *

RectangleMap = List[List[Tile]]


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


def parse_map(
    lines: Iterable[str],
    sharing: bool = True,
    karel: Karel = None,
    new_style_map: bool = False,
) -> Tuple[Karel, RectangleMap]:
    """ Take a filepath to map file and make a robot and a map.

    Args:
        lines: of the map, e.g. open file or ['>.', '.1']
        sharing: uses a shared constants for tiles (except Beeper)
        karel: use this karel instead (better warning)
        new_style_map: space separated tiles and specified Karel and dimensions.
    Raises:
        RobotError: on incorrect map
    Returns:
        pair of Karel and RectangleMap
    """
    karel_set = karel
    make_tile = one_tile if sharing else lambda cls: cls()

    def parse_tile(char, x, y):
        nonlocal karel  # better then reading twice

        if char in Karel.CHARS:
            if karel is None:
                karel = Karel(Point(x=x, y=y), char)
            elif not karel_set:  # another Karel on map
                raise RobotError(f"Karel is already on {karel.position}.")
            return make_tile(Empty)

        for tile in map(make_tile, [Empty, Wall, Treasure]):
            if char in tile.chars:
                return tile
        try:
            count = int(char)
            if count > 0:
                return Beeper(count=count)
        except ValueError:
            pass
        # else no match
        raise RobotError(f"Invalid token '{char}' on line {y} column {x}.")

    def get_tiles(line):
        if new_style_map:
            return line.split()  # this allows larger number of beepers
        return list(line.strip())

    lines = iter(lines)
    if new_style_map:
        karel = parse_new_map_header(next(lines)) or karel
    karel_map = [
        [parse_tile(char, x, y) for x, char in enumerate(get_tiles(line))]
        for y, line in enumerate(lines)
    ]

    if karel is None:
        raise RobotError("Karel must be present on the map!")

    if any(len(x) != len(karel_map[0]) for x in karel_map):
        raise RobotError("Karel map must be a rectangle!")

    return karel, karel_map
