#!/usr/bin/env python
from board import Board, LogicException
import sys
import os

# this needs to be smarter soon
if len(sys.argv) > 1:
    _board = Board(sys.argv[1])
else:
    _board = Board(os.path.join('levels', '09_newspaper.karelmap'))

def refresh(func):
    try:
        res = func()
        _board.draw()
        return res
    except LogicException as e:
        _board.draw_exception(e)
    except Exception as e:
        raise e

def move(): refresh(_board.move)
def turn_left(): refresh(_board.turn_left)
def pick_beeper(): refresh(_board.pick_beeper)
def put_beeper(): refresh(_board.put_beeper)
def front_is_clear(): return _board.front_is_clear()
def right_is_clear(): return _board.right_is_clear()
def left_is_clear(): return _board.left_is_clear()
def beeper_is_present(): return _board.beeper_is_present()
def facing_north(): return _board.facing_north()
def facing_south(): return _board.facing_south()
def facing_east(): return _board.facing_east()
def facing_west(): return _board.facing_west()
def set_speed(spd): _board.set_speed(spd)