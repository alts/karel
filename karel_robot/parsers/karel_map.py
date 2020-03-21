from typing import Tuple, List
from ..tiles import *
from ..robot import *

RectangleMap = List[List[Tile]]


def parse_new_map_header(line: str, no_error: bool = False):
    form = "KAREL X Y > B"
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
            raise RobotError(f"Map header not in form '{form}'")


def parse_map(
    path: str,
    sharing: bool = True,
    karel: Karel = None,
    no_error: bool = False,
    new_style_map: bool = False,
) -> Tuple[Karel, RectangleMap]:
    """ Take a filepath to map file and make a robot and a map.

    Args:
        path: path to map file, e.g. levels/00_window.karelmap
        sharing: uses a shared constants for tiles (except Beeper)
        karel: use this karel instead (better warning)
        no_error: skip errors (good for overriding Karel's position)
        new_style_map: space separated tiles and specified Karel and dimensions.
    Raises:
        RuntimeError: on incorrect map
    Returns:
        pair of Karel and RectangleMap
    """
    make_tile = one_tile if sharing else lambda cls: cls()

    def parse_tile(char, x, y):
        nonlocal karel  # better then reading twice

        if char in Karel.CHARS and not new_style_map:
            if karel is not None:
                if no_error:
                    return make_tile(Empty)
                raise RobotError(f"Karel is already on {karel.position}.")
            karel = Karel(Point(x=x, y=y), Karel.DIRECTIONS[char])
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
        if no_error:
            return make_tile(Empty)
        raise RobotError(
            f"invalid character '{char}' in {path} " f"on line {y} column {x}"
        )

    def get_tiles(line):
        if new_style_map:
            return line.split()  # this allows larger number of beepers
        return list(line.strip())

    with open(path, "r") as f:
        if new_style_map:
            if karel and not no_error:
                raise RobotError(
                    "Karel already defined! "
                    "To skip map header, run with '--ignore_robot_errors'"
                )
            elif not karel:
                karel = parse_new_map_header(f.readline())
        karel_map = [
            [parse_tile(char, x, y) for x, char in enumerate(get_tiles(line))]
            for y, line in enumerate(f)
        ]

    if not no_error and karel is None:
        raise RobotError("Karel must be present on the map!")

    if not no_error and any(len(x) != len(karel_map[0]) for x in karel_map):
        raise RobotError("Karel map must be a rectangle!")

    return karel, karel_map
