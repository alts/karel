#!/usr/bin/env python3
"""Program Karel to search for treasure.

The idea is from a paper on cooperative education in CS1:
https://dl.acm.org/doi/abs/10.1145/2492686
"""
from karel_robot.run import *

while not front_is_blocked():
    move()

while not front_is_treasure():
    turn_left()
    if front_is_blocked():
        turn_left()
    # FIX: add else
    move()
    turn_right()
