# Karel the Robot (Code)

This directory contains the code behind Karel.

In here you will find the objects that store information about
the loaded map, robot's position and manage the (cursed) screen.

If you like OOP you can write programs like this:
```python
import karel_robot as robot
import karel_robot.parsers as robot_parsers

karel, karelmap = robot_parsers.parse_map("worlds/00_window.karelmap")
w = robot.Window(karel=karel, tiles=karelmap)
w.pause()
w.move()
w.karel.turn_left()
w.move()
w.draw()
```

## Run

The file `karel_run.py` in `run` directory parses the command line
and starts the program. It also defines useful functions for writing
one's own Karel programs, like `move()` or `turn_left()`, which
make the above program much simpler:

```python
from karel_robot.run import *

move()
turn_left()
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
python3 karel_robot/run/karel_run.py levels/00_window.karelmap
```