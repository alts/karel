""" Example code with karel_robot.run functions.
"""
from karel_robot.run import *

# you can call imported functions
turn_left()

# or use Python, like branching ('if') or logical 'not'
if not front_is_blocked():
    move()

