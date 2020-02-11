# Karel (now in Python)

> Karel is a pretty snazzy environment for learning to program. You can [read about it here](http://en.wikipedia.org/wiki/Karel_(programming_language\)).
> I decided to write a Karel environment for Python, after seeing that all of the others had too many dependencies for beginners.
>
> Stephen Altamirano (`alts/karel`)

## Write simple Karel programs

Writing in Python is super fast and easy! Save a `YOUR_PROGRAM.py` text file in this folder, import all the functions and start writing code!

```python
from karel_run import *

## Simple program ##

move()
turn_left()
move()
```

> For a true linux executable, add the [shebang](https://stackoverflow.com/a/19305076/11105559), then the right to execute with `chmod +x YOUR_PROGRAM.py` and run it as `./YOUR_PROGRAM.py`.

## Karel functions

These are the functions exported by `karel_run.py`. Note that the map is loaded and screen started in the moment of `from karel_run import *`. If you only need raw objects and methods see `karel.py`.

```python
# Movement
move()       # Karel moves in the direction he is facing
turn_left()  # Karel turns left
turn_right() # Karel turns right
pause()      # Pause execution, press any key to continue
stop()       # End execution
# Beepers
pick_beeper() # Karel tries to pick up a beeper
put_beeper()  # Karel puts down a beeper (if he has any)
beeper_is_present() # True if Karel stands on a beeper
# Walls
front_is_blocked()  # True if Karel can't move forward
front_is_treasure() # True if Karel is standing in front of a Treasure
# Direction
facing_north()  # True if Karel is facing north (^)
facing_south()  #                         south (v)
facing_east()   #                          east (>)
facing_west()   #                          west (<)
# Settings
set_speed(100)   # How fast Karel moves, 0 to 100
set_karel_beepers(None)  # Set Karel's beepers, 0+ and None means inf
```

## Karel world

Karel maps are also simple text files and look like this one:

    1..#...
    #....^.

Karel is represented by the arrow. There are two walls (`#`) and one beeper in the upper right corner (`1`).

> Planing to write maps? Check out the vim highlighting! :)


## Run your program

Open the terminal and write this command:

```bash
python3 YOUR_PROGRAM.py YOUR_MAP.karelmap
```

Press `Q` to quit or `P` to pause program.
Program pauses when Karel tries to make an illegal move.

## Try out your map with *interactive*

Use the command:
```bash
python3 karel_run.py YOUR_MAP.karelmap
```

You can now use your keyboard to control Karel.

    ⬆ ... move()
    ⬅ ... turn_left()
    ⮕ ... turn_right()
    I  ... pick_beeper()
    U  ... put_beeper()

## Examples

### Simple program

Make a couple of moves, turn three times and try to move.
If the first movements or last picking beeper raises
an Exception then the program will be paused until any
key is pressed (`Q` still quits however).

```python
from karel_run import *

# Simple Karel program
move()
move()
turn_left()
turn_left()
turn_left()
if not front_is_blocked():
    move()
else:
    pick_beeper()
```

### Introduction

Run this with worlds `00` - `02_window`, Karel will walk to the wall and then search for a treasure in the walls.

```python
from karel_run import *

while not front_is_blocked():
    move()

while not front_is_treasure():
    turn_left()
    if front_is_blocked():
        turn_left()
    # FIX: add else
    move()
    turn_right()
```

The idea comes from a [paper on cooperative learning in CS1](https://dl.acm.org/doi/abs/10.1145/2492686).


### Langton

This makes Karel a [Langton's ant](https://en.wikipedia.org/wiki/Langton%27s_ant), using a single beeper to mark a tile as "Black" or picks it up to make it "White".

```python
from karel_run import *

set_speed(100)

while True:
    if not beeper_is_present():  # At a white square
        put_beeper()  # flip the color of the square
        turn_right()  # turn 90° right
        move()        # move forward one unit
    else:  # At a black square
        pick_beeper() # flip the color of the square
        turn_left()   # turn 90° left
        move()        # move forward one unit
```

The ant moves seemingly randomly, but makes a nice picture in about 11000 steps. Try with the world `12_140x50.karelmap`.

