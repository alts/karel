from karel_robot.board import *


def test_empty():
    m = KarelMap()
    for x in range(-1, 2):
        for y in range(-1, 2):
            assert m[x, y] == Empty(), "Should be empty infinite map"
