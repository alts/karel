from karel_run import *

set_speed(100)

while True:
    # At a white square, turn 90° right, flip the color of the square, move forward one unit
    if not beeper_is_present():
        put_beeper()
        turn_right()
        move()
    # At a black square, turn 90° left, flip the color of the square, move forward one unit
    else:
        pick_beeper()
        turn_left()
        move()
