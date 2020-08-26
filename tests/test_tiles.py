from karel_robot.tiles import Tile, Empty, Wall, Treasure, Beeper


def test_str():
    for t in Empty, Wall, Treasure, Beeper:
        assert len(str(t())) == 1, "Tile string not 1 character"


def test_str_beeper():
    b = Beeper()
    for i in range(1, 11):
        b.count = i
        assert len(str(b)) == 1, "Beeper string not 1 character"
