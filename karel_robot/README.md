# Karel the Robot (Code)

This directory contains the code behind Karel.

In here you will find the objects that store information about
the loaded map, robot's position and manage the (cursed) screen.

If you like OOP you can write programs like this:
```python
from karel_robot import WindowOpen
from karel_robot.parsers import MapParser


def example(window):
    window.karel.turn_left()

    while not window.front_is_blocked():
        window.move()


def main():
    with open("../world/1_window.km") as m:
        m = MapParser(lines=m, new_style_map=False)

    with WindowOpen(
        karel=m.karel, tiles=m.karel_map, x_map=m.width, y_map=m.height
    ) as w:
        example(w)
        w.draw()


if __name__ == "__main__":
    main()
```

## Run

The file `karel_run.py` in `run` directory parses the command line
and starts the program. It also defines useful functions for writing
one's own Karel programs, like `move()` or `turn_left()`, which
make the above program much simpler:

```python
from karel_robot.run import *

turn_left()
while not front_is_blocked():
    move()
```

Running this code with `python3 example_run.py levels/00_window.karelmap`
is probably better unless you want to implement some special behaviour.
For example the longer code does not redraw the map with each step.
The smaller one does so, but only the tiles Karel was standing on.

### Interactive

The `karel_run.py` is used to create a standalone executable, with
which users can try out maps and command Karel using a keyboard.

If you cloned this repository you can install it yourself:
```bash
pip3 install .  # use the path to this repo in place of . if different
```

Or run it directly:
```bash
python3 karel_robot/run/karel_run.py levels/1_window.karelmap
```