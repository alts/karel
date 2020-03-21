"""Example code with more OOP approach.
"""
from karel_robot import Window
from karel_robot.parsers import parse_map


def main():
    """This is how you could use the classes to do the same as `example.py`.

    This approach gives more power to the user, namely it allows to draw
    on screen when needed. Note however that the whole screen is redrawn,
    instead of only the last tile.
    """
    karel, karelmap = parse_map("levels/00_window.karelmap")
    w = Window(karel=karel, tiles=karelmap)
    w.pause()
    w.move()
    w.karel.turn_left()
    w.move()
    w.draw()


if __name__ == '__main__':
    main()
