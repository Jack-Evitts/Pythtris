import tkinter as tk
import pygame as pg
import sys
import random

### Stopped Let's code: Tetris episode 11 by TigerhawkT3 at 01:27:06


class Shape:
    def __init__(self, shape, key, piece, row, column, coords):
        self.shape = shape
        self.key = key
        self.piece = piece
        self.row = row
        self.column = column
        self.coords = coords


class Tetris:
    def __init__(self, parent):
        self.debug = 'debug' in sys.argv[1:]
        parent.title('Pytris')
        self.parent = parent
        self.board_width = 10
        self.board_height = 24
        self.high_score = 0
        self.width = 200
        self.height = 480
        self.square_width = self.width//10
        self.shapes = {'S':[['*', ''],
                            ['*', '*'],
                            ['', '*']],
                       'Z':[['', '*'],
                            ['*', '*'],
                            ['*', '']],
                       'J':[['*', '*'],
                            ['*', ''],
                            ['*', '']],
                       'L':[['*', ''],
                            ['*', ''],
                            ['*', '*']],
                       'O':[['*', '*'],
                            ['*', '*']],
                       'I':[['*'],
                            ['*'],
                            ['*'],
                            ['*']],
                       'T':[['*', '*', '*'],
                            ['', '*', '']]
                      }
        self.colours = {'S': '#6495ED',
                        'Z': '#F08080',
                        'J': '#B0C4DE',
                        'L': '#FFDAB9',
                        'O': '#DB7093',
                        'I': '#BA55D3',
                        'T': '#40E0D0'}
        self.parent.bind('<Down>', self.shift)
        self.parent.bind('<Left>', self.shift)
        self.parent.bind('<Right>', self.shift)
        self.parent.bind('<Up>', self.rotate)
        self.parent.bind('a', self.snap)
        self.parent.bind('A', self.snap)
        self.parent.bind('d', self.snap)
        self.parent.bind('D', self.snap)
        self.parent.bind('s', self.snap)
        self.parent.bind('S', self.snap)
        self.parent.bind('<Escape>', self.pause)
        self.parent.bind('<Control-n>', self.draw_board)
        self.parent.bind('<Control-N>', self.draw_board)
        self.canvas = None
        self.preview_canvas = None
        self.ticking = None
        self.spawning = None
        self.score_var = tk.StringVar()
        self.score_label = tk.Label(ROOT,
                                    textvariable=self.score_var,
                                    width=25,
                                    height=5,
                                    font=('Helvetica', 12))
        self.score_label.grid(row=2, column=1, sticky="S")
        self.high_score_var = tk.StringVar()
        self.high_score_var.set('High Score:\n0')
        self.high_score_label = tk.Label(ROOT,
                                         textvariable=self.high_score_var,
                                         width=25,
                                         height=5,
                                         font=('Helvetica', 12))
        self.high_score_label.grid(row=3, column=1, sticky="N")
        self.preview_label = tk.Label(ROOT,
                                      text='Next Piece',
                                      width=25,
                                      height=5,
                                      font=('Helvetica', 12))
        self.preview_label.grid(row=0, column=1, sticky="S")
        self.draw_board()


    def tick(self):
        if self.piece_is_active:
            self.shift()
        self.ticking = self.parent.after(self.tickrate, self.tick)


    def shift(self, event=None):
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        direction = (event and event.keysym) or 'Down'
        # use event-keysym to check event/direction
        if direction == 'Down':
            rt = r+1  # row temporary
            ct = c  # column temporary

        elif direction == 'Left':
            rt = r
            ct = c-1
        elif direction == 'Right':
            rt = r
            ct = c+1

        success = self.check_and_move(self.active_piece.shape, rt, ct, l, w)

        if direction in 'Down' and not success:
            self.settle()


    def draw_board(self, event=None):
        if self.ticking:
            self.parent.after_cancel(self.ticking)
        if self.spawning:
            self.parent.after_cancel(self.spawning)
        self.score_var.set('Score:\n0')
        self.board = [['' for column in range(self.board_width)]
                      for row in range(self.board_height)]
        self.field = [[None for column in range(self.board_width)] for row in range(self.board_height)]
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(ROOT, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, rowspan=4)
        self.border = self.canvas.create_rectangle(2,
                                                   2,
                                                   self.width - 2,
                                                   self.height - 2,
                                                   width=2)
        self.h_separator = self.canvas.create_line(0,
                                                   self.height//6,
                                                   self.width,
                                                   self.height//6,
                                                   width=2)
        self.v_separator = self.canvas.create_line(self.width,
                                                   0,
                                                   self.width,
                                                   self.height,
                                                   width=2)
        if self.preview_canvas:
            self.preview_canvas.destroy()
        self.preview_canvas = tk.Canvas(ROOT,
                                        width=5*self.square_width,
                                        height=5*self.square_width)
        self.preview_canvas.grid(row=1, column=1)
        self.tickrate = 1000
        self.score = 0
        self.piece_is_active = False
        self.paused = False
        self.preview()
        self.spawning = self.parent.after(self.tickrate, self.spawn)
        self.ticking = self.parent.after(self.tickrate*2, self.tick)

    def pause(self, event=None):
        if self.piece_is_active and not self.paused:
            self.paused = True
            self.piece_is_active = False
            self.parent.after_cancel(self.ticking)
        elif self.paused:
            self.paused = False
            self.piece_is_active = True
            self.ticking = self.parent.after(self.tickrate, self.tick)


    def print_board(self):
        for row in self.board:
            print(*(cell or ' ' for cell in row))


    def check(self, shape, r, c, l, w):
        for row, squares in zip(range(r, r+l), shape):
            for column, square in zip(range(c, c+w), squares):
                if ((row not in range(self.board_height))
                        or (column not in range(self.board_width))
                        or (square and self.board[row][column] == 'x')):
                    return
        return True


    def move(self, shape, r, c, l, w):
        square_idxs = iter(range(4))

        for row in self.board:
            row[:] = ['' if cell == '*' else cell for cell in row]

        for row, squares in zip(range(r, r+l), shape):
            for column, square in zip(range(c, c+w), squares):
                if square:
                    self.board[row][column] = square
                    square_idx = next(square_idxs)
                    coord = (column*self.square_width,
                             row*self.square_width,
                             (column+1)*self.square_width,
                             (row+1)*self.square_width)
                    self.active_piece.coords[square_idx] = coord
                    self.canvas.coords(self.active_piece.piece[square_idx], coord)
        self.active_piece.row = r
        self.active_piece.column = c
        self.active_piece.shape = shape
        if self.debug:
            self.print_board()
        return True


    def check_and_move(self, shape, r, c, l, w):
        if self.check(shape, r, c, l, w):
            self.move(shape, r, c, l, w)
            return True


    def rotate(self, event=None):
        if not self.active_piece:
            return
        if len(self.active_piece.shape) == len(self.active_piece.shape[0]):
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        x = c + w//2
        y = r + l//2
        direction = event.keysym
        '''if direction in ('a', 'A'):  # left
            shape = rotate_array(self.active_piece.shape, -90)
            rotation_index = (self.active_piece.rotation_index - 1) % 4
            ra, rb = self.active_piece.rotation[rotation_index]
            rotation_offsets = -ra, -rb
        else:  # right'''
        shape = rotate_array(self.active_piece.shape, 90)
        rotation_index = self.active_piece.rotation_index
        rotation_offsets = self.active_piece.rotation[rotation_index]
        rotation_index = (rotation_index + 1) % 4

        l = len(shape)
        w = len(shape[0])
        rt = y - l//2
        ct = x - w//2
        x_correction, y_correction = rotation_offsets
        rt += y_correction
        ct += x_correction

        success = self.check_and_move(shape, rt, ct, l, w)
        if not success:
            return

        self.active_piece.rotation_index = rotation_index


    def settle(self):
        self.piece_is_active = False

        for row in self.board:
            row[:] = ['x' if cell == '*' else cell for cell in row]

        self.print_board()

        for (x1, y1, x2, y2), id in zip(self.active_piece.coords, self.active_piece.piece):
            self.field[y1//self.square_width][x1//self.square_width] = id

        indices = [idx for idx, row in enumerate(self.board) if all(row)]
        if indices:
            self.score += (40, 100, 300, 1200)[len(indices) - 1]
            self.clear(indices)
            if all(not cell for row in self.board for cell in row):
                self.score += 2000
            self.high_score = max(self.score, self.high_score)
            self.score_var.set(f"Score:\n{self.score}")
            self.high_score_var.set(f"High Score:\n{self.high_score}")

        if any(any(row) for row in self.board[:4]):
            self.lose()
            return

        self.spawning = self.parent.after(self.tickrate, self.spawn)


    def preview(self):
        self.preview_canvas.delete(tk.ALL)
        key = random.choice('IJLOSTZ')
        shape = rotate_array(self.shapes[key], random.choice((0, 90, 180, 270)))
        self.preview_piece = Shape(shape, key, [], 0, 0, [])
        width = len(shape[0])
        half = self.square_width//2

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.preview_piece.coords.append((self.square_width*x + half,
                                                      self.square_width*y + half,
                                                      self.square_width*(x+1) + half,
                                                      self.square_width*(y+1) + half))
                    self.preview_piece.piece.append(self.preview_canvas.create_rectangle(self.preview_piece.coords[-1],
                                                                                         fill=self.colours[key],
                                                                                         width=2))
        self.preview_piece.rotation_index = 0
        self.preview_piece.i_nudge = (len(shape) < len(shape[0])) and 4 in (len(shape), len(shape[0]))
        self.preview_piece.row = self.preview_piece.i_nudge
        if 3 in (len(shape), len(shape[0])):
            self.preview_piece.rotation = [(0, 0),
                                          (1, 0),
                                          (-1, 1),
                                          (0, -1)]
        else:
            self.preview_piece.rotation = [(1, -1),
                                          (0, 1),
                                          (0, 0),
                                          (-1, 0)]
        if len(shape) < len(shape[0]):
            self.preview_piece.rotation_index += 1


    def spawn(self):
        self.piece_is_active = True
        self.active_piece = self.preview_piece
        self.preview()
        width = len(self.active_piece.shape[0])
        start = (10-width)//2
        self.active_piece.column = start
        self.active_piece.start = start
        self.active_piece.coords = []
        self.active_piece.piece = []
        for y, row in enumerate(self.active_piece.shape):
            self.board[y+self.active_piece.i_nudge][start:start+width] = self.active_piece.shape[y]
            for x, cell in enumerate(row, start=start):
                if cell:
                    self.active_piece.coords.append((self.square_width*x,
                                                     self.square_width*(y+self.active_piece.i_nudge),
                                                     self.square_width*(x+1),
                                                     self.square_width*(y+self.active_piece.i_nudge+1)))
                    self.active_piece.piece.append(self.canvas.create_rectangle(self.active_piece.coords[-1],
                                                                                fill=self.colours[self.active_piece.key],
                                                                                width=2))
        if self.debug:
            self.print_board()


    def lose(self):
        self.piece_is_active = False
        self.parent.after_cancel(self.ticking)
        self.clear_iter(range(len(self.board)))


    def snap(self, event=None):
        down = {'s', 'S'}
        left = {'a', 'A'}
        right = {'d', 'D'}
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])

        direction = event.keysym

        while 1:
            if self.check(self.active_piece.shape,
                            r+(direction in down),
                            c + (direction in right) - (direction in left),
                            l,
                            w):
                r += direction in down
                c += (direction in right) - (direction in left)
            else:
                break
        self.move(self.active_piece.shape, r, c, l, w)
        if direction in down:
            self.settle()


    def clear(self, indices):
        for idx in indices:
            self.board.pop(idx)
            self.board.insert(0, ['' for column in range(self.board_width)])
        self.clear_iter(indices)


    def clear_iter(self, indices, current_column=0):
        for row in indices:
            if row%2:
                cc = current_column
            else:
                cc = self.board_width - current_column - 1
            id = self.field[row][cc]
            self.field[row][cc] = None
            self.canvas.delete(id)
        if current_column < self.board_width-1:
            self.parent.after(50, self.clear_iter, indices, current_column+1)
        else:
            for idx, row in enumerate(self.field):
                offset = sum(r > idx for r in indices)*self.square_width
                for square in row:
                    if square:
                        self.canvas.move(square, 0, offset)
            for row in indices:
                self.field.pop(row)
                self.field.insert(0, [None for x in range(self.board_width)])


def rotate_array(array, angle, wide=False):
    '''
    Rotates a rectangular or diamond 2D array in increments of 45 degrees.
    Parameters:
        array (list): a list containing sliceable sequences, such as list, tuple, or str
        angle (int): a positive angle for rotation, in 45-degree increments.
        wide (bool): whether a passed diamond array should rotate into a wide array
            instead of a tall one (tall is the default). No effect on square matrices.
    '''
    angle = angle%360
    if angle < 1:
        return [list(row) for row in array]
    lengths = list(map(len, array))
    rect = len(set(lengths)) == 1
    width = max(lengths)
    height = sum(lengths)/width
    if wide:
        width, height = height, width
    if not rect:
        array = [list(row) for row in array]
        array = [[array[row+col].pop() for row in range(width)] for col in range(height)]
        angle += 45
    nineties, more = divmod(angle, 90)
    if nineties == 3:
        array = list(zip(*array))[::-1]
    else:
        for i in range(nineties):
            array = list(zip(*array[::-1]))
    if more:
        ab = abs(len(array)-len(array[0]))
        m = min(len(array), len(array[0]))
        tall = len(array) > len(array[0])
        array = [[array[r][c] for r,c in zip(range(row-1, -1, -1), range(row))
                 ] for row in range(1, m+1)
           ] + [[array[r][c] for r,c in zip(range(m-1+row*tall, row*tall-1, -1),
                                            range(row*(not tall), m+row*(not tall)+1))
                ] for row in range(1, ab+(not tall))
           ] + [[array[r][c] for r,c in zip(range(len(array)-1, ab*tall+row-1, -1),
                                            range(ab*(not tall)+row, len(array[0])+(not tall)))
                ] for row in range((not tall), m)
           ]
    return array


ROOT = tk.Tk()
TETRIS = Tetris(ROOT)
ROOT.mainloop()