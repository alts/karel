"""Example code with more OOP approach.
"""
import karel_robot as robot


def main():
    """This is how you could use the classes to do the same as `example.py`.

    This approach gives more power to the user, namely it allows to draw
    on screen when needed. Note however that the whole screen is redrawn,
    instead of only the last tile.
    """
    karel, karelmap = robot.parse_map("levels/00_window.karelmap")
    w = robot.Window(karel=karel, karel_map=karelmap)
    w.pause()
    w.move()
    w.karel.turn_left()
    w.move()
    w.draw()


if __name__ == '__main__':
    main()
