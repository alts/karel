# This is the example file from main.py
from karel_robot.run import *

# moves to the wall, places one beeper and stops
while not front_is_blocked():
    move()

put_beeper()
