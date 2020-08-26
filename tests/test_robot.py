from karel_robot.robot import *


def test_karel_dir():
    k = Karel()
    for d in k.INV_DIR:
        k.facing = d
        assert len(k.to_dir()) == 1, "Karel should have one character direction string"
