""" Example code with more OOP approach. """
from karel_robot import WindowOpen
from karel_robot.parsers import MapParser


def example(window):
    window.karel.turn_left()

    while not window.front_is_blocked():
        window.move()


def main():
    """ This is how you could use the classes to do the same as `example.py`.

    This approach gives more power to the user. Notice the board is redrawn
    only after Karel reaches the wall.

    Also it might just be safer then leaving it to Python garbage collector ;)
    """
    with open("../world/M3_div.km2") as m:
        m = MapParser(lines=m, new_style_map=True)

    with WindowOpen(
        karel=m.karel, tiles=m.karel_map, x_map=m.width, y_map=m.height
    ) as w:
        example(w)
        w.draw()


if __name__ == "__main__":
    main()
