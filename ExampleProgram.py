#!/usr/bin/env python
from runner import *


#move()
#turn_left()
#pick_beeper()
#put_beeper()
#front_is_clear() -> bool
#right_is_clear() -> bool
#left_is_clear() -> bool
#beeper_is_present() -> bool
#facing_north() -> bool
#facing_south() -> bool
#facing_east() -> bool
#facing_west() -> bool
#set_speed(spd) (Valid speeds are 0 through 100)

set_speed(50)

move()
move()
turn_left()
turn_left()
turn_left()
if front_is_clear():
    move()
else:
    pick_beeper()