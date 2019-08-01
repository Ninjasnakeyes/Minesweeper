"""
Components/functions:
    -update only when mouse click
    -number clicks
    -open zeroes (updated: took out nested for loops, added ripple clear [will add toggle instant/ripple clear])
    -toggle flag/can't open flagged
    -first click never mine
    -keeps highscore from previous program opening
    -new highscore asks name
    -3 different default sizes
    -customizable size/# of mines
    -if size > certain value: shrink size
    -if size < beginner lv: tile size same but hud size doesn't change

"""

import pygame
import random
import pickle
import os
import sys

# Globals
beginner = (8, 8)
intermediate = (16, 16)
expert = (16, 31)

size = 32
hud = size * 2
mode = ""

# Puts screen in middle
os.environ['SDL_VIDEO_CENTERED'] = '1'


def knight_check(x, y, row, col, field):
    check, r, c = [], len(field), len(field[1])
    for i in row:
        for j in col:
            if i != x and j != y:
                if i < x and j < y:
                    if 0 <= i - 1 < r and 0 <= j < c and field[i - 1][j] != -1:
                        check.append((i - 1, j))
                    if 0 <= i < r and 0 <= j - 1 < c and field[i][j - 1] != -1:
                        check.append((i, j - 1))
                elif i < x and j > y:
                    if 0 <= i - 1 < r and 0 <= j < c and field[i - 1][j] != -1:
                        check.append((i - 1, j))
                    if 0 <= i < r and 0 <= j + 1 < c and field[i][j + 1] != -1:
                        check.append((i, j + 1))
                elif i > x and j > y:
                    if 0 <= i + 1 < r and 0 <= j < c and field[i + 1][j] != -1:
                        check.append((i + 1, j))
                    if 0 <= i < r and 0 <= j + 1 < c and field[i][j + 1] != -1:
                        check.append((i, j + 1))
                elif i > x and j < y:
                    if 0 <= i + 1 < r and 0 <= j < c and field[i + 1][j] != -1:
                        check.append((i + 1, j))
                    if 0 <= i < r and 0 <= j - 1 < c and field[i][j - 1] != -1:
                        check.append((i, j - 1))
    return check


class Tile(pygame.sprite.Sprite):
    def __init__(self, r, c, xpos, ypos, s, value):
        pygame.sprite.Sprite.__init__(self)
        self.value = value
        self.s = s
        self.i = r
        self.j = c
        self.x = xpos
        self.y = ypos
        self.die = self.open = self.flag = self.added = self.add_flag = self.checked = False
        self.image = pygame.Surface((self.s, self.s)).convert()
        self.rect = pygame.Rect(xpos, ypos, self.s, self.s)
        self.image = pygame.image.load("images/tile.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.s, self.s))

    def zero(self, board):
        row_range = range(self.i - 1, self.i + 2)
        col_range = range(self.j - 1, self.j + 2)
        if mode != 'knightsweeper':
            for i in row_range:
                for j in col_range:
                    if 0 <= i < len(board) and 0 <= j < len(board[0]):
                        if board[i][j].open is False and board[i][j].flag is False:
                            self.image = pygame.image.load("images/open.jpg").convert_alpha()
                            self.image = pygame.transform.scale(self.image, (self.s, self.s))
                            board[i][j].open = True
                            board[i][j].reveal(board)
        elif mode == 'knightsweeper':
            check = knight_check(self.i, self.j, row_range, col_range, board)
            r, c = len(board), len(board[1])

            for i in check:
                if 0 <= i[0] < r and 0 <= i[1] < c and board[i[0]][i[1]] != -1:
                    self.image = pygame.image.load("images/open.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
                    board[i[0]][i[1]].open = True
                    board[i[0]][i[1]].reveal(board)
        self.checked = True

    def reveal(self, board, z=False):
        self.open = True
        if self.value == -1:
            self.die = True
            self.image = pygame.image.load("images/redmine.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
            return True
        elif self.value > 0:
            self.image = pygame.image.load("images/" + str(self.value) + ".jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
        elif self.value == 0:
            self.image = pygame.image.load("images/open.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
            if z:
                self.zero(board)

    def num_open(self, board):
        nflag = 0
        row_range = range(self.i - 1, self.i + 2)
        col_range = range(self.j - 1, self.j + 2)

        if mode != 'knightsweeper':
            for i in row_range:
                for j in col_range:
                    if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j].flag:
                        nflag += 1

            if nflag == self.value:
                for i in row_range:
                    for j in col_range:
                        if 0 <= i < len(board) and 0 <= j < len(board[0]) and not board[i][j].flag:
                            if board[i][j].reveal(board):
                                self.die = True

        elif mode == 'knightsweeper':
            check = knight_check(self.i, self.j, row_range, col_range, board)
            r, c = len(board), len(board[1])

            for i in check:
                if 0 <= i[0] < r and 0 <= i[1] < c and board[i[0]][i[1]].flag:
                    nflag += 1

            if nflag == self.value:
                for i in check:
                    if 0 <= i[0] < r and 0 <= i[1] < c and not board[i[0]][i[1]].flag:
                        if board[i[0]][i[1]].reveal(board):
                            self.die = True

    def toggle_flag(self):
        if self.flag is False:
            self.flag = True
            self.image = pygame.image.load("images/flag.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
        elif self.flag is True:
            self.flag = False
            self.image = pygame.image.load("images/tile.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))

    def clicked_on(self, click):
        pos = pygame.mouse.get_pos()
        if self.rect.left < pos[0] < self.rect.right and self.rect.top < pos[1] < self.rect.bottom:
            if click == 1 or click == 3 and click != "type of click":
                return True
            else:
                return False

    def update(self, click, dead, win, board):
        if dead and self.value == -1 and self.open is False and self.flag is False:
            self.image = pygame.image.load("images/mine.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
        elif win and self.value == -1 and self.open is False:
            self.image = pygame.image.load("images/flag.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
        elif dead and self.value != -1 and self.flag is True:
            self.image = pygame.image.load("images/wrongmine.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.s, self.s))

        if dead is False and win is False:
            if self.clicked_on(click):
                if self.open is False:
                    if click == 3 and self.open is False:
                        self.toggle_flag()
                    elif click == 1 and self.flag is False:
                        return self.reveal(board)

                elif self.open and click == 1 and self.value > 0:
                    self.num_open(board)


class Border(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, height, w, i):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((height, w))
        self.image = pygame.image.load("images/" + i + ".jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (height, w))
        self.rect = pygame.Rect(xpos, ypos, height, w)


class Text:
    def __init__(self, scale, text, xpos, ypos, color):
        self.font = pygame.font.SysFont("Britannic Bold", scale)
        self.image = self.font.render(text, 1, color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(xpos, ypos)


class Hud(pygame.sprite.Sprite):
    def __init__(self, n, sw, x, s, value, w, i=""):
        pygame.sprite.Sprite.__init__(self)
        self.value = value
        self.s = s
        self.n = n
        if self.value == "counter" or self.value == "timer":
            self.x = x
            self.image = pygame.image.load("images/" + i + ".jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(self.s/2 + 2), self.s))
            self.rect = pygame.Rect(0, 0, self.s, self.s)
            self.rect.centery = hud / 2
            if self.value == "counter":
                self.rect.left = (s/2 + 2) + x
            elif self.value == "timer":
                self.rect.right = (sw - 2) - x
        elif self.value == "face":
            self.rect = pygame.Rect(0, 0, self.s, self.s)
            self.rect.center = (w/2 + self.s/2, hud/2)
            if mode == '':
                self.image = pygame.image.load("images/happy.jpg").convert_alpha()
            if mode == "wrapfield":
                self.image = pygame.image.load("images/wrapface.jpg").convert_alpha()
            if mode == "knightsweeper":
                self.image = pygame.image.load("images/happy.jpg").convert_alpha()
                self.image.fill((0, 0, 0))
            self.image = pygame.transform.scale(self.image, (self.s, self.s))
        elif self.value == "scores":
            self.rect = pygame.Rect(0, 0, self.s + self.s/2, self.s)
            self.rect.center = (((self.s/2 + 36)+(w/2 + self.s))/2 - 5, hud/2)
            self.image = pygame.image.load("images/tile.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(self.s + self.s/2), int(self.s)))

    def mouse_on(self):
        pos = pygame.mouse.get_pos()
        if self.rect.left < pos[0] < self.rect.right and self.rect.top < pos[1] < self.rect.bottom:
            return True
        else:
            return False

    def update(self, win, dead, click, num_mines="", time=""):
        if self.value == "counter":
            if self.n == 2:
                if win:
                    self.image = pygame.image.load("images/hud0.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
                elif "-" not in num_mines:
                    self.image = pygame.image.load("images/hud" + num_mines[len(num_mines) - 1]+".jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
            elif self.n == 1:
                if len(num_mines) == 1 or win:
                    self.image = pygame.image.load("images/hud0.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
                elif len(num_mines) >= 2 and "-" not in num_mines:
                    self.image = pygame.image.load("images/hud" + num_mines[len(num_mines) - 2]+".jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
            elif self.x == 0:
                if len(num_mines) == 1 or len(num_mines) == 2 or win:
                    self.image = pygame.image.load("images/hud0.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
                elif len(num_mines) == 3 and "-" not in num_mines:
                    self.image = pygame.image.load("images/hud" + num_mines[len(num_mines) - 3]+".jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))

        elif self.value == "timer" and int(time) <= 999:
            if self.n == 0:
                self.image = pygame.image.load("images/hud" + time[len(time) - 1] + ".jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
            elif self.n == 1 and len(time) > 1:
                self.image = pygame.image.load("images/hud" + time[len(time) - 2] + ".jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))
            elif self.n == 2 and len(time) > 2:
                self.image = pygame.image.load("images/hud" + time[len(time) - 3] + ".jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(self.s / 2 + 2), self.s))

        elif self.value == "face":
            if mode == '':
                if dead:
                    self.image = pygame.image.load("images/dead.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
                elif win:
                    self.image = pygame.image.load("images/win.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
                elif pygame.mouse.get_pressed() != (0, 0, 0):
                    self.image = pygame.image.load("images/scared.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
                else:
                    self.image = pygame.image.load("images/happy.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
            elif mode == 'wrapfield':
                if dead:
                    self.image.fill((0, 0, 0))
                else:
                    self.image = pygame.image.load("images/wrapface.jpg").convert_alpha()
                    self.image = pygame.transform.scale(self.image, (self.s, self.s))
            elif mode == 'knightsweeper':
                if dead:
                    self.image.fill((255, 0, 0))
                else:
                    self.image.fill((0, 0, 0))

            if self.mouse_on():
                if click == 1:
                    return 'left'
                elif click == 3:
                    return 'right'

        elif self.value == "scores":
            if pygame.mouse.get_pressed() == (1, 0, 0) and self.mouse_on():
                self.image = pygame.image.load("images/open.jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(self.s + self.s/2), int(self.s)))
            else:
                self.image = pygame.image.load("images/tile.jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(self.s + self.s/2), int(self.s)))

            if self.mouse_on() and click is 1:
                return True


def gen_level(small, w, h, diff, num_mines, group, s, p, first_r=None, first_c=None, o_field=None):
    row = r = diff[0]
    col = c = diff[1]
    x = xcor = s / 2
    y = s * 2

    if small:
        x_center = s / 2
        y_center = 0
        if r % 2 == 0:
            x_center = 0
        if c % 2 == 0:
            y_center = s / 2

        x = xcor = w / 2 - (s * (row / 2) + x_center)
        y = h / 2 - (s * (col / 2) - y_center)

    if first_r is None or first_c is None:
        field = [[0 for i in range(c)] for j in range(r)]

        for mine in range(num_mines):
            t = True
            while t:
                m = (random.randrange(r), random.randrange(c))
                if m not in p:
                    p.append(m)
                    t = False

            mine_x = p[mine][0]
            mine_y = p[mine][1]
            field[mine_x][mine_y] = -1

            row_range = range(mine_x - 1, mine_x + 2)
            col_range = range(mine_y - 1, mine_y + 2)

            if mode != 'knightsweeper':
                for i in row_range:
                    for j in col_range:
                        if 0 <= i < r and 0 <= j < c and field[i][j] != -1:
                            field[i][j] += 1
                        if mode == 'wrapfield':
                            wrap = False
                            wi, wj = i, j
                            if i < 0:
                                wi = r - 1
                                wrap = True
                            elif i == r:
                                wi = 0
                                wrap = True
                            if j < 0:
                                wj = c - 1
                                wrap = True
                            elif j == c:
                                wj = 0
                                wrap = True
                            if field[wi][wj] != -1 and wrap:
                                field[wi][wj] += 1
            elif mode == 'knightsweeper':
                check = knight_check(mine_x, mine_y, row_range, col_range, field)

                for i in check:
                    if 0 <= i[0] < r and 0 <= i[1] < c and field[i[0]][i[1]] != -1:
                        field[i[0]][i[1]] += 1

        field2 = [[0 for i in range(c)] for j in range(r)]

        r = c = 0
        for tile in field:
            for value in tile:
                t = Tile(r, c, x, y, s, value)
                field2[r][c] = t
                group.add(t)
                x += s
                c += 1
            y += s
            x = xcor
            r += 1
            c = 0

        # for i in range(len(field)):
        #    print(field[i])

        return field2, field
    else:
        field = o_field

        field[first_r][first_c] = 0
        for i in p:
            if i[0] == first_r and i[1] == first_c:
                p.remove(i)
        for i in range(r):
            for j in range(c):
                if field[i][j] > 0:
                    field[i][j] = 0

        row_range = range(first_r - 1, first_r + 2)
        col_range = range(first_c - 1, first_c + 2)

        chosen = False
        for i in row_range:
            for j in col_range:
                if i == first_r and j == first_c:
                    break
                if 0 <= i < r and 0 <= j < c and field[i][j] != -1:
                    field[i][j] = -1
                    p.append((i, j))
                    chosen = True
                    break
            if chosen:
                break
        if chosen is False:
            t = True
            while t:
                cont = True
                m = (random.randrange(r), random.randrange(c))
                if m[0] == first_r and m[1] == first_c:
                    cont = False
                if cont and field[m[0]][m[1]] != -1:
                    field[m[0]][m[1]] = -1
                    p.append(m)
                    t = False

        for mine in range(num_mines):
            mine_x = p[mine][0]
            mine_y = p[mine][1]

            row_range = range(mine_x - 1, mine_x + 2)
            col_range = range(mine_y - 1, mine_y + 2)

            if mode != 'knightsweeper':
                for i in row_range:
                    for j in col_range:
                        if 0 <= i < r and 0 <= j < c and field[i][j] != -1:
                            field[i][j] += 1
                        if mode == 'wrapfield':
                            wrap = False
                            wi, wj = i, j
                            if i < 0:
                                wi = r - 1
                                wrap = True
                            elif i == r:
                                wi = 0
                                wrap = True
                            if j < 0:
                                wj = c - 1
                                wrap = True
                            elif j == c:
                                wj = 0
                                wrap = True
                            if field[wi][wj] != -1 and wrap:
                                field[wi][wj] += 1
            elif mode == 'knightsweeper':
                check = knight_check(mine_x, mine_y, row_range, col_range, field)

                for i in check:
                    if 0 <= i[0] < r and 0 <= i[1] < c and field[i[0]][i[1]] != -1:
                        field[i[0]][i[1]] += 1

        field2 = [[0 for i in range(c)] for j in range(r)]

        r = c = 0
        for tile in field:
            for value in tile:
                t = Tile(r, c, x, y, s, value)
                if t.i == first_r and t.j == first_c:
                    t.open = True
                    t.reveal(None)
                field2[r][c] = t
                group.add(t)
                x += s
                c += 1
            y += s
            x = xcor
            r += 1
            c = 0

        return field2


def gen_border(r, c, s, w, sw, hud_height, border_group, hud_group):
    # Border array
    b = [["HL"]]
    for i in range(c * 2):
        b[0].append("HM")
    b[0].append("HR")

    for i in range(r * 2):
        bm = ["ML"]
        for j in range(c * 2):
            bm.append(" ")
        bm.append("MR")
        b.append(bm)

    bb = ["BL"]
    for i in range(c * 2):
        bb.append("BM")
    bb.append("BR")
    b.append(bb)

    # Add Border
    b_size = int(s/2)
    x = y = 0
    for r in b:
        for c in r:
            if c == "HL":
                p = Border(x, y, b_size, hud_height, "HL")
                border_group.add(p)
            elif c == "HM":
                p = Border(x, y, b_size, hud_height, "HM")
                border_group.add(p)
            elif c == "HR":
                p = Border(x, y, b_size, hud_height, "HR")
                border_group.add(p)
            elif c == "ML":
                p = Border(x, y, b_size, b_size, "ML")
                border_group.add(p)
            elif c == "MR":
                p = Border(x, y, b_size, b_size, "MR")
                border_group.add(p)
            elif c == "BL":
                p = Border(x, y, b_size, b_size, "BL")
                border_group.add(p)
            elif c == "BM":
                p = Border(x, y, b_size, b_size, "BM")
                border_group.add(p)
            elif c == "BR":
                p = Border(x, y, b_size, b_size, "BR")
                border_group.add(p)
            x += b_size
        if c == "HR":
            y += hud_height
        else:
            y += b_size
        x = 0

    # Hud
    face = Hud(None, sw, 0, s, "face", w, "")
    hud_group.add(face)
    scores = Hud(None, sw, 0, s, "scores", w, "tile")
    hud_group.add(scores)

    xpos = n = 0
    for i in range(3):
        counter = Hud(n, sw, xpos, s, "counter", w, "hud0")
        hud_group.add(counter)
        xpos += s/2 + 2
        n += 1

    xpos = n = 0
    for i in range(3):
        timer = Hud(n, sw, xpos, s, "timer", w, "hud0")
        hud_group.add(timer)
        xpos += s/2 + 2
        n += 1


def update_score(score):
    b_high = i_high = e_high = "None"
    b_name = i_name = e_name = ""
    if type(score) is list and type(score) is list:
        if len(score[0]) != 0:
            if min(score[0]) < 60:
                b_high = str(min(score[0])) + " secs"
            else:
                b_high = str(int(min(score[0]) / 60)) + " mins " + str(int(min(score[0]) % 60)) + " secs"

        if len(score[1]) != 0:
            i_name = score[4]
            if min(score[1]) < 60:
                i_high = str(min(score[1])) + " secs"
            else:
                i_high = str(int(min(score[1]) / 60)) + " mins " + str(int(min(score[1]) % 60)) + " secs"

        if len(score[2]) != 0:
            e_name = score[5]
            if min(score[2]) < 60:
                e_high = str(min(score[2])) + " secs"
            else:
                e_high = str(int(min(score[2]) / 60)) + " mins " + str(min(score[2]) % 60) + " secs"
        if len(score[3]) != 0:
            b_name = score[3]
        if len(score[4]) != 0:
            i_name = score[4]
        if len(score[5]) != 0:
            e_name = score[5]

    return b_high, i_high, e_high, b_name, i_name, e_name


def blit_box(screen, scale, pos):
    box = pygame.Surface((scale[0] + 3, scale[1] + 3)).convert()
    box.fill((0, 0, 0))
    box_rect = box.get_rect()
    box_rect.center = pos
    screen.blit(box, box_rect)
    box1 = pygame.Surface(scale).convert()
    box1.fill((193, 193, 193))
    box1_rect = box1.get_rect()
    box1_rect.center = pos
    screen.blit(box1, box1_rect)


def main():
    # Init var
    pygame.init()
    global beginner, intermediate, expert, size, hud, mode

    s_width = 288
    s_height = 288
    pygame.display.set_caption('MINESWEEPER')
    screen = pygame.display.set_mode((s_width, s_height), pygame.SRCALPHA)

    fps = 60
    clock = pygame.time.Clock()
    diff = beginner
    local_size = size
    mines = 10
    score = None
    intro = True
    play = ripple = face_click = False

    # Game loops
    while intro:
        # Intro attributes
        intro_pic = pygame.image.load("images/intro.jpg").convert_alpha()
        intro_pic = pygame.transform.scale(intro_pic, (300, 300))
        intro_rect = intro_pic.get_rect()
        intro_rect.center = (s_width/2, s_height/2)

        color = (255, 0, 0)
        title = Text(55, "Minesweeper", 0, s_height/2 + 10, color)
        title.rect.centerx = s_width/2

        subtitle = Text(35, "--Click to Start--", 0, s_height/2 + 45, color)
        subtitle.rect.centerx = s_width/2

        t_name = Text(23, "Developer: Kyle Leksmana", 0, s_height/2 + 120, color)
        t_name.rect.centerx = s_width/2

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                intro = False
                play = True

        # Blit
        screen.fill((49, 47, 49))
        screen.blit(intro_pic, intro_rect)
        screen.blit(title.image, title.rect)
        screen.blit(t_name.image, t_name.rect)
        screen.blit(subtitle.image, subtitle.rect)

        # Fps limiter
        clock.tick(fps)
        # Writes to main surface
        pygame.display.flip()

    while play:
        woon = 0

        # Screen setup
        row, col = diff
        hud = local_size * 2
        if row < 8 or col < 8:
            w = h = (8 * local_size)
            small = True
        else:
            w = (col * local_size)
            h = (row * local_size)
            small = False
        s_width = int(w + local_size)
        s_height = int(h + local_size / 2 + hud)
        screen = pygame.display.set_mode((s_width, int(s_height + hud)), pygame.SRCALPHA)

        # Vars
        new_r = new_c = new_mines = name = ""
        first = True
        passed_time = chose = clear = skip_count = 0
        not_flagged = mines
        start = restart = win = dead = show_score = q = saved = fastest = False
        start_time = pygame.time.get_ticks()

        xdisplays = (local_size/2 + 36 + w/2 + local_size)
        text = Text(22, "Clear all tiles without mines to win", 0, 0, (0, 0, 0))
        text.rect.center = (s_width/2, s_height + hud/4 - 6)
        text1 = Text(18, '"q" = quit|"r"/face button = restart|', 0, 0, (0, 0, 0))
        text1.rect.center = (s_width/2, s_height + hud/2 - 6)
        text2 = Text(18, '"t" = toggle ripple/instant reveal', 0, 0, (0, 0, 0))
        text2.rect.center = (s_width/2, s_height + hud/2 + 9)
        text3 = Text(18, '"1"/"2"/"3"/"Enter" = change size', 0, 0, (0, 0, 0))
        text3.rect.center = (s_width/2, s_height + hud/2 + 23)
        button = Text(17, "Scores", 0, 0, (0, 0, 0))
        button.rect.center = (xdisplays/2 - 5, hud/2)

        # Score
        if os.path.isfile("scores.pickle") is not False:
            p_in = open("scores.pickle", "rb")
            score = pickle.load(p_in)
            p_in.close()

            if len(score) >= 6:
                if score[3] == "wrapfield- " and score[4] == "wrapfield- " and score[5] == "wrapfield- " and face_click:
                    mode = "wrapfield"
                    face_click = False
                else:
                    face_click = False

        b_high, i_high, e_high, b_name, i_name, e_name = update_score(score)

        # Groups
        p = []
        tile_group = pygame.sprite.Group()
        b_group = pygame.sprite.Group()
        hud_group = pygame.sprite.Group()

        # Level setup
        board, field = gen_level(small, s_width, s_height + local_size/2, diff, mines, tile_group, local_size, p)
        if small:
            gen_border(8, 8, local_size, w, s_width, hud, b_group, hud_group)
        else:
            gen_border(row, col, local_size, w, s_width, hud, b_group, hud_group)

        while restart is False:
            # In game setup
            new_diff = None
            if woon == 3:
                win = True
                for t in tile_group:
                    if t.value != -1:
                        t.reveal(board)
            if chose == 0:
                new_r = new_c = new_mines = ''

            # Timer
            if not win and not dead:
                if start is False:
                    start_time = pygame.time.get_ticks()
                if start:
                    passed_time = int((pygame.time.get_ticks() - start_time)/1000)

            # Mode
            if not_flagged == diff[0] * diff[1] * -1 + mines:
                if mode == '':
                    mode = 'knightsweeper'
                    restart = True
                elif mode == 'knightsweeper':
                    mode = ''
                    restart = True

            # Input
            click = "type of click"
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        q = True
                    elif event.key == pygame.K_r and fastest is False:
                        restart = True
                    elif event.key == pygame.K_t and chose == 0 and fastest is False:
                        ripple = not ripple
                    elif event.key == pygame.K_SLASH and woon < 3 and not win:
                        woon += 1
                    elif event.key == pygame.K_k:
                        if mode != "knightsweeper":
                            mode = "knightsweeper"
                        else:
                            mode = ''
                    elif event.key == pygame.K_1:
                        if fastest:
                            if len(name) <= 15:
                                name += "1"
                        elif chose == 0:
                            new_diff = beginner
                            local_size = size
                            restart = True
                        elif chose == 1 and len(new_r) <= 2:
                            new_r += "1"
                        elif chose == 2 and len(new_c) <= 2:
                            new_c += "1"
                        elif chose == 3 and len(new_mines) <= 3:
                            new_mines += "1"
                    elif event.key == pygame.K_2:
                        if fastest:
                            if len(name) <= 15:
                                name += "2"
                        elif chose == 0:
                            new_diff = intermediate
                            local_size = size
                            restart = True
                        elif chose == 1 and len(new_r) <= 2:
                            new_r += "2"
                        elif chose == 2 and len(new_c) <= 2:
                            new_c += "2"
                        elif chose == 3 and len(new_mines) <= 3:
                            new_mines += "2"
                    elif event.key == pygame.K_3:
                        if fastest:
                            if len(name) <= 15:
                                name += "3"
                        elif chose == 0:
                            new_diff = expert
                            local_size = size
                            restart = True
                        elif chose == 1 and len(new_r) <= 2:
                            new_r += "3"
                        elif chose == 2 and len(new_c) <= 2:
                            new_c += "3"
                        elif chose == 3 and len(new_mines) <= 3:
                            new_mines += "3"
                    if chose != 0 or fastest:
                        if event.key == pygame.K_4:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "4"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "4"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "4"
                            elif fastest and len(name) <= 15:
                                name += "4"
                        elif event.key == pygame.K_5:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "5"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "5"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "5"
                            elif fastest and len(name) <= 15:
                                name += "5"
                        elif event.key == pygame.K_6:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "6"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "6"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "6"
                            elif fastest and len(name) <= 15:
                                name += "6"
                        elif event.key == pygame.K_7:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "7"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "7"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "7"
                            elif fastest and len(name) <= 15:
                                name += "7"
                        elif event.key == pygame.K_8:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "8"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "8"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "8"
                            elif fastest and len(name) <= 15:
                                name += "8"
                        elif event.key == pygame.K_9:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "9"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "9"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "9"
                            elif fastest and len(name) <= 15:
                                name += "9"
                        elif event.key == pygame.K_0:
                            if chose == 1 and len(new_r) <= 2:
                                new_r += "0"
                            elif chose == 2 and len(new_c) <= 2:
                                new_c += "0"
                            elif chose == 3 and len(new_mines) <= 3:
                                new_mines += "0"
                            elif fastest and len(name) <= 15:
                                name += "0"
                    if fastest and len(name) <= 15:
                        if event.key == pygame.K_q:
                            name += "q"
                        elif event.key == pygame.K_w:
                            name += "w"
                        elif event.key == pygame.K_e:
                            name += "e"
                        elif event.key == pygame.K_r:
                            name += "r"
                        elif event.key == pygame.K_t:
                            name += "t"
                        elif event.key == pygame.K_y:
                            name += "y"
                        elif event.key == pygame.K_u:
                            name += "u"
                        elif event.key == pygame.K_i:
                            name += "i"
                        elif event.key == pygame.K_o:
                            name += "o"
                        elif event.key == pygame.K_p:
                            name += "p"
                        elif event.key == pygame.K_a:
                            name += "a"
                        elif event.key == pygame.K_s:
                            name += "s"
                        elif event.key == pygame.K_d:
                            name += "d"
                        elif event.key == pygame.K_f:
                            name += "f"
                        elif event.key == pygame.K_g:
                            name += "g"
                        elif event.key == pygame.K_h:
                            name += "h"
                        elif event.key == pygame.K_j:
                            name += "j"
                        elif event.key == pygame.K_k:
                            name += "k"
                        elif event.key == pygame.K_l:
                            name += "l"
                        elif event.key == pygame.K_z:
                            name += "z"
                        elif event.key == pygame.K_x:
                            name += "x"
                        elif event.key == pygame.K_c:
                            name += "c"
                        elif event.key == pygame.K_v:
                            name += "v"
                        elif event.key == pygame.K_b:
                            name += "b"
                        elif event.key == pygame.K_n:
                            name += "n"
                        elif event.key == pygame.K_m:
                            name += "m"
                    if event.key == 8:
                        if chose == 1:
                            new_r = new_r[:-1]
                        if chose == 2:
                            new_c = new_c[:-1]
                        if chose == 3:
                            new_mines = new_mines[:-1]
                        if fastest:
                            name = name[:-1]
                    if event.key == pygame.K_RETURN:
                        if show_score is False and fastest is False:
                            chose += 1
                            if len(new_r) != 0:
                                if int(new_r) <= 1 or int(new_r) > 50:
                                    new_r = ''
                                    chose = 0
                            if len(new_c) != 0:
                                if int(new_c) <= 1 or int(new_c) > 100:
                                    new_c = ''
                                    chose = 0
                            if len(new_mines) != 0:
                                if int(new_mines) == 0:
                                    new_r = new_c = ''
                                    chose = 0
                            if len(new_r) != 0 and len(new_c) != 0:
                                if chose == 4:
                                    if int(new_r) > 44 or int(new_c) > 79:
                                        new_diff = (int(new_r), int(new_c))
                                        local_size = int(size/4 + size/5)
                                        restart = True
                                    elif int(new_r) > 32 or int(new_c) > 60:
                                        new_diff = (int(new_r), int(new_c))
                                        local_size = int(size/3 + size/4)
                                        restart = True
                                    elif int(new_r) >= 23 or int(new_c) >= 59:
                                        new_diff = (int(new_r), int(new_c))
                                        local_size = int(size/2 + size/4)
                                        restart = True
                                    elif int(new_r) < 23 and int(new_c) < 44:
                                        new_diff = (int(new_r), int(new_c))
                                        local_size = size
                                        restart = True
                            elif chose == 4:
                                chose = 0
                        if fastest and len(name) != 0:
                            fastest = False
                            if diff == beginner:
                                score[3] = name + "- "
                            if diff == intermediate:
                                score[4] = name + "- "
                            if diff == expert:
                                score[5] = name + "- "
                            p_out = open("scores.pickle", "wb")
                            pickle.dump(score, p_out)
                            p_out.close()
                            b_high, i_high, e_high, b_name, i_name, e_name = update_score(score)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = event.button
                    woon = 0

            # Update
            if chose == 0:
                check = True
                if show_score is False and click != 'type of click':
                    repeat = True
                    while repeat:
                        repeat = False
                        for t in tile_group:
                            u = t.update(click, dead, win, board)
                            if t.checked:
                                check = False
                            if t.die or t.open and t.value == -1:
                                dead = True
                            if t.value != -1 and t.open and t.added is False:
                                clear += 1
                                first = False
                                t.added = True
                            if u and t.open:
                                if first is False:
                                    dead = True
                                elif t.clicked_on(click) and first:
                                    dead = first = False
                                    i, j = t.i, t.j
                                    for T in tile_group:
                                        T.kill()
                                    board = gen_level(small, s_width, s_height + local_size/2, diff, mines, tile_group, local_size, p, i, j, field)
                                    repeat = True
                            if t.clicked_on(click):
                                first = False
                                start = True
                            if t.flag and t.clicked_on and t.add_flag is False:
                                not_flagged -= 1
                                t.add_flag = True
                            elif t.flag is False and t.clicked_on and t.add_flag:
                                not_flagged += 1
                                t.add_flag = False

                if row * col < intermediate[0] * intermediate[1]:
                    skip_speed = 5
                elif intermediate[0] * intermediate[1] <= row * col < expert[0] * expert[1]:
                    skip_speed = 3
                else:
                    skip_speed = 1

                if skip_count % skip_speed == 0:
                    skip = True
                else:
                    skip = False

                if check and ripple and skip:
                    for t in tile_group:
                        if t.value == 0 and t.open and t.checked is False:
                            t.reveal(board, True)
                        if t.value != -1 and t.open and t.added is False:
                            clear += 1
                            first = False
                            t.added = True
                skip_count += 1

                if ripple is False:
                    for i in range(21):
                        for t in tile_group:
                            if t.value == 0 and t.open and t.checked is False:
                                t.reveal(board, True)
                            if t.value != -1 and t.open and t.added is False:
                                clear += 1
                                first = False
                                t.added = True

                if clear == (row * col) - mines:
                    win = True
                if win or dead:
                    for t in tile_group:
                        t.update(click, dead, win, board)

                for h in hud_group:
                    if click != 'type of click' or not win or not dead:
                        if h.value == "face":
                            if h.update(win, dead, click) == 'left':
                                restart = True
                                h.kill()
                            elif h.update(win, dead, click) == 'right':
                                face_click = restart = True
                                h.kill()
                        elif h.value == "scores":
                            if h.update(win, dead, click):
                                show_score = not show_score
                    if h.value == "timer" and win is False and dead is False:
                        h.update(win, dead, click, str(not_flagged), str(passed_time))
                    elif h.value == "counter" and dead is False:
                        h.update(win, dead, click, str(not_flagged), str(passed_time))

            # Blit
            screen.fill((193, 193, 193))
            screen.blit(text.image, text.rect)
            screen.blit(text1.image, text1.rect)
            screen.blit(text2.image, text2.rect)
            screen.blit(text3.image, text3.rect)

            rippletext = "Instant"
            if ripple:
                rippletext = "Ripple"
            elif ripple is False:
                rippletext = "Instant"
            textz = Text(20, rippletext, 0, 0, (0, 0, 255))
            textz.rect.center = (xdisplays - 20, hud / 2)

            for b in b_group:
                screen.blit(b.image, b.rect)
            for t in tile_group:
                screen.blit(t.image, t.rect)
            for h in hud_group:
                screen.blit(h.image, h.rect)
            screen.blit(button.image, button.rect)
            screen.blit(textz.image, textz.rect)

            # Boxes
            if chose == 1 or chose == 2 or show_score or fastest:
                show = True
            elif chose == 3 and len(new_r) != 0 and len(new_c) != 0:
                show = True
            else:
                show = False
                chose = 0
            if show:
                # Display box
                scale, pos = (s_width / 2 + 120, s_height / 4), (s_width / 2, s_height / 2)
                box = pygame.Surface((scale[0] + 3, scale[1] + 3)).convert()
                box.fill((0, 0, 0))
                box_rect = box.get_rect()
                box_rect.center = pos
                screen.blit(box, box_rect)
                box1 = pygame.Surface(scale).convert()
                box1.fill((193, 193, 193))
                box1_rect = box1.get_rect()
                box1_rect.center = pos
                screen.blit(box1, box1_rect)

            if 0 < chose < 4:
                # Text box
                scale, pos = (50, 25), (s_width / 2 + 100, s_height / 2)
                if chose == 3:
                    scale, pos = (65, 25), (s_width / 2 + 90, s_height / 2)
                box = pygame.Surface((scale[0] + 3, scale[1] + 3)).convert()
                box.fill((0, 0, 0))
                box_rect = box.get_rect()
                box_rect.center = pos
                screen.blit(box, box_rect)
                box1 = pygame.Surface(scale).convert()
                box1.fill((193, 193, 193))
                box1_rect = box1.get_rect()
                box1_rect.center = pos
                screen.blit(box1, box1_rect)
            if woon == 3:
                ww = Text(80, "SHAME", 0, 0, (255, 0, 0))
                ww.rect.center = (s_width/2, s_height/2)
                screen.blit(ww.image, ww.rect)

            # Save score
            if win and saved is False:
                if diff == beginner or diff == intermediate or diff == expert:
                    saved = True
                    if os.path.isfile("scores.pickle") is not False and score is not None and start:
                        if len(score[0]) != 0 or len(score[1]) != 0 or len(score[2]) != 0:
                            if diff == beginner:
                                if len(score[0]) != 0:
                                    if passed_time < min(score[0]):
                                        fastest = True
                                score[0].append(passed_time)
                            elif diff == intermediate:
                                if len(score[1]) != 0:
                                    if passed_time < min(score[1]):
                                        fastest = True
                                score[1].append(passed_time)
                            elif diff == expert:
                                if len(score[2]) != 0:
                                    if passed_time < min(score[2]):
                                        fastest = True
                                score[2].append(passed_time)
                    elif os.path.isfile("scores.pickle") is False:
                        if diff == beginner:
                            score = [[passed_time], [], [], "", "", ""]
                        elif diff == intermediate:
                            score = [[], [passed_time], [], "", "", ""]
                        elif diff == expert:
                            score = [[], [], [passed_time], "", "", ""]

                b_high, i_high, e_high, b_name, i_name, e_name = update_score(score)
                p_out = open("scores.pickle", "wb")
                pickle.dump(score, p_out)
                p_out.close()

            # Text
            if row * col <= beginner[0] * beginner[1]:
                font = 23
            elif beginner[0] * beginner[1] < row * col <= intermediate[0] * intermediate[1]:
                font = 27
            else:
                font = 31
            if show_score and not fastest:
                beginner_score = Text(font, "Beginner Best: " + b_name + b_high, 0, 0, (0, 0, 0))
                beginner_score.rect.center = (s_width/2, s_height/2 - 20)
                screen.blit(beginner_score.image, beginner_score.rect)
                intermediate_score = Text(font, "Intermediate Best: " + i_name + i_high, 0, 0, (0, 0, 0))
                intermediate_score.rect.center = (s_width/2, s_height/2)
                screen.blit(intermediate_score.image, intermediate_score.rect)
                expert_score = Text(font, "Expert Best: " + e_name + e_high, 0, 0, (0, 0, 0))
                expert_score.rect.center = (s_width/2, s_height/2 + 20)
                screen.blit(expert_score.image, expert_score.rect)

            if chose == 1 and not fastest:
                r = Text(35, "Custom Row: ", 0, 0, (0, 0, 0))
                r.rect.center = (s_width/2 - 15, s_height/2)
                screen.blit(r.image, r.rect)
                nr = Text(35, str(new_r), 0, 0, (0, 0, 0))
                nr.rect.center = (s_width/2 + 100, s_height/2)
                screen.blit(nr.image, nr.rect)
                r2 = Text(30, "Max: 50", 0, 0, (0, 0, 0))
                r2.rect.center = (s_width/2, s_height/2 + 20)
                screen.blit(r2.image, r2.rect)

            elif chose == 2 and not fastest:
                c = Text(35, "Custom Col: ", 0, 0, (0, 0, 0))
                c.rect.center = (s_width/2 - 15, s_height/2)
                screen.blit(c.image, c.rect)
                cr = Text(35, str(new_c), 0, 0, (0, 0, 0))
                cr.rect.center = (s_width/2 + 100, s_height/2)
                screen.blit(cr.image, cr.rect)
                c2 = Text(30, "Max: 100", 0, 0, (0, 0, 0))
                c2.rect.center = (s_width/2, s_height/2 + 20)
                screen.blit(c2.image, c2.rect)

            elif chose == 3 and not fastest and len(new_r) != 0 and len(new_c) != 0:
                m = Text(35, "Custom Mines: ", 0, 0, (0, 0, 0))
                m.rect.center = (s_width/2 - 28, s_height/2)
                screen.blit(m.image, m.rect)
                mr = Text(35, str(new_mines), 0, 0, (0, 0, 0))
                mr.rect.center = (s_width/2 + 90, s_height/2)
                screen.blit(mr.image, mr.rect)
                m2 = Text(28, "Max: " + str((int(new_r) * int(new_c)) - 1), 0, 0, (0, 0, 0))
                m2.rect.center = (s_width/2, s_height/2 + 20)
                screen.blit(m2.image, m2.rect)
                m3 = Text(25, "(Leave blank for auto)", 0, 0, (0, 0, 0))
                m3.rect.center = (s_width/2, s_height/2 + 35)
                screen.blit(m3.image, m3.rect)

            elif fastest and mode == '':
                d = diff
                if diff == beginner:
                    d = "beginner"
                if diff == intermediate:
                    d = "intermediate"
                if diff == expert:
                    d = "expert"
                n = Text(23, "You have the fastest time for " + d, 0, 0, (0, 0, 0))
                n.rect.center = (s_width/2, s_height/2 - 10)
                screen.blit(n.image, n.rect)
                n2 = Text(23, "Please enter your name:", 0, 0, (0, 0, 0))
                n2.rect.center = (s_width/2, s_height/2 + 7)
                screen.blit(n2.image, n2.rect)
                n3 = Text(23, str(name), 0, 0, (0, 0, 0))
                n3.rect.center = (s_width/2, s_height/2 + 23)
                screen.blit(n3.image, n3.rect)

            # New game
            if q:
                pygame.quit()
                sys.exit()
            elif new_diff is not None:
                diff = new_diff
                if new_r != '' and new_c != '' and new_mines != '':
                    if int(new_mines) < (int(new_r) * int(new_c)):
                        mines = int(new_mines)
                    else:
                        mines = int((diff[0] * diff[1]) * 0.15625)
                        if mines == 0:
                            mines = 1
                else:
                    mines = int((diff[0] * diff[1]) * 0.15625)
                    if mines == 0:
                        mines = 1

            # Fps limiter
            clock.tick(fps)
            # Writes to main surface
            pygame.display.flip()


if __name__ == '__main__':
    main()
