#!/usr/bin/env python3
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

