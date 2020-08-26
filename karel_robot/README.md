# Karel the Robot (Code)

This directory contains the code behind Karel.

In here you will find the objects that store information about
the loaded map, robot's position and manage the (cursed) screen.

If you like OOP you can write programs like this:
```python
from karel_robot import WindowOpen
from karel_robot.parsers import MapParser

def example(window):
    while not window.front_is_blocked():
        window.move()
    window.put_beeper()

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

In the `run` directory many simple and useful functions are
defined, including the actual `main()` function in `main.py`
which parses the command line and starts the `karel` program. 

If you cloned this repository you can install it yourself:
```bash
pip3 install .  # use the path to this repo in place of . if different
```

Or run it directly:
```bash
python3 karel_robot/run/karel_run.py world/1_window.karelmap
```

### Functions

The file `functions.py` defines useful functions for writing
one's own Karel programs, like `move()` or `turn_left()`, which
make the above program much simpler:

```python
from karel_robot.run import *

while not front_is_blocked():
    move()

put_beeper()
```

Running this code with `python3 walk.py world/1_window.karelmap`
is probably better unless you want to implement some custom behaviour.
For example the longer code only draws the map once Karel is finished.
The smaller redraws with each step, but only the tiles Karel moves to/from.

### Interactive

The `interactive.py` is used in the `karel` executable, so that
users can command Karel using a keyboard.

|     Key    |  Function       |
|------------|-----------------|
|<kbd>↑</kbd>| `move()`        |
|<kbd>←</kbd>| `turn_left()`   |
|<kbd>→</kbd>| `turn_right()`  |
|<kbd>I</kbd>| `pick_beeper()` |
|<kbd>U</kbd>| `put_beeper()`  |
|<kbd>Q</kbd>| `stop()`        |

It is also useful for manual testing and defines several cheats:

|             Key             | Function                                             |
| :-------------------------: | ---------------------------------------------------- |
| <kbd>0</kbd> - <kbd>9</kbd> | Sets the tile Karel stands on to *n* **beepers**     |
|        <kbd>$</kbd>         | Sets the tile in front of Karel to a **treasure**    |
|        <kbd>#</kbd>         | Sets the tile in front of Karel to a **wall**        |
|        <kbd>.</kbd>         | Sets the tile in front of Karel to an **empty tile** |
|        <kbd>V</kbd>         | Toggle status line verbosity                         |
|        <kbd>R</kbd>         | Force resize of the window                           |
|        <kbd>I</kbd>         | **Stop interactive** mode                            |
