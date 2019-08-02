#!/usr/bin/env python
import curses
import time
from karel import Karel

class LogicException(Exception):
    pass

class Board(object):
    KAREL_CHARS = '<^>v'
    BEEPER_CHAR = 'o'
    speed = 50

    def __init__(self, map_path):
        self.map = None
        self.karel = None
        self.screen = None
        self.beepers = []
        self.construct_map(map_path)

    def __enter__(self):
        self.start_screen()
        return self

    def __exit__(self, *args):
        self.end_screen()

    def start_screen(self):
        self.screen = curses.initscr()
        curses.start_color()
        # wall
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
        # Karel
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # beeper
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # Karel on beeper
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    def end_screen(self):
        time.sleep((100.0-self.speed)/100.0)
        curses.endwin()

    def construct_map(self, map_path):
        directions = {
            '>': (1, 0),
            '^': (0, 1),
            '<': (-1, 0),
            'v': (0, -1),
        }

        map = [[]]
        with open(map_path, 'rb') as f:
            for y, line in enumerate(f):
                row = []
                for x, char in enumerate(line.strip()):
                    char = chr(char)
                    if char in self.KAREL_CHARS:
                        self.karel = Karel((x + 1, y + 1), directions[char])
                        char = '.'
                    elif char == self.BEEPER_CHAR:
                        self.beepers.append((x + 1, y + 1))
                        char = '.'
                    row.append(char)
                map.append(['#'] + row + ['#'])

        map.append([])
        for _ in range(len(map[1])):
            map[0].append('#')
            map[-1].append('#')
        self.map = map

    def draw(self):
        screen = self.screen

        for y, row in enumerate(self.map):
            for x, char in enumerate(row):
                args = [y + 1, x, char]
                if char == '#':
                    args.append(curses.color_pair(1))
                elif char == 'o':
                    args.append(curses.color_pair(3))
                screen.addstr(*args)

        beeper_color = curses.color_pair(3)
        for bx, by in self.beepers:
            screen.addstr(by + 1, bx, 'o', beeper_color)

        screen.addstr(
            self.karel.position[1] + 1,
            self.karel.position[0],
            self.karel_char(),
            curses.color_pair(4) if self.beeper_is_present() else curses.color_pair(2)
        )

        screen.addstr(y + 4, 0, ' ')
        screen.refresh()
        screen.nodelay(True)
        time.sleep((100.0-self.speed)/100.0)
        ch = screen.getch()
        screen.nodelay(False)
        if ch != -1 and chr(ch) == 'c':
            exit(1)
    
    def set_speed(self, spd):
        if spd < 0:
            spd = 0
        elif spd > 100:
            spd = 100
        self.speed = spd

    def draw_exception(self, exception):
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        self.screen.addstr(0, 0, str(exception), curses.color_pair(5))
        ch = self.screen.getch()
        if chr(ch) is 'c':
            exit(1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLACK)
        self.screen.addstr(0, 0, str(exception), curses.color_pair(6))

    def karel_char(self):
        # index will be in (-2, -1, 1, 2)
        index = self.karel.facing[0] + 2*self.karel.facing[1]
        return ' >v^<'[index]

    # Karel passthroughs
    def move(self):
        if not self.front_is_clear():
            raise LogicException('Can\'t move. There is a wall in front of Karel')
        self.karel.move()

    def turn_left(self):
        self.karel.turn_left()

    def pick_beeper(self):
        position = self.karel.position
        for i, coord in enumerate(self.beepers):
            if coord == self.karel.position:
                del self.beepers[i]
                self.karel.pick_beeper()
                break
        else:
            raise LogicException('Can\'t pick beeper from empty location')


    def put_beeper(self):
        if not self.holding_beepers():
            raise LogicException('Can\'t put beeper. Karel has none')
        self.beepers.append(self.karel.position)
        self.karel.put_beeper()

    # world conditions
    def front_is_clear(self):
        next_x = self.karel.position[0] + self.karel.facing[0]
        next_y = self.karel.position[1] + self.karel.facing[1]
        return self.map[next_y][next_x] == '.'

    def left_is_clear(self):
        next_x = self.karel.position[0] + self.karel.facing[1]
        next_y = self.karel.position[1] - self.karel.facing[0]
        return self.map[next_y][next_x] == '.'

    def right_is_clear(self):
        next_x = self.karel.position[0] - self.karel.facing[1]
        next_y = self.karel.position[1] + self.karel.facing[0]
        return self.map[next_y][next_x] == '.'

    def facing_north(self):
        return self.karel.facing[1] == -1

    def facing_south(self):
        return self.karel.facing[1] == 1

    def facing_east(self):
        return self.karel.facing[0] == 1

    def facing_west(self):
        return self.karel.facing[0] == -1

    def beeper_is_present(self):
        return self.karel.position in self.beepers

    def holding_beepers(self):
        return self.karel.holding_beepers()