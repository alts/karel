#!/usr/bin/env python3
"""Make Karel move like Langton's ant.
"""
from karel_robot.run import *

set_speed(None)
# toggle_status_line(quiet=True)

while True:  # repeat
    if beeper_is_present():  # At a black square
        pick_beeper()  # flip the color of the square
        turn_left()  # turn 90° left
        move()  # move forward one unit
    else:  # At a white square
        put_beeper()  # flip the color of the square
        turn_right()  # turn 90° right
        move()  # move forward one unit
