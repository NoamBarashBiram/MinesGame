#!/usr/bin/env python3

from random import randint
from os import system, mkdir
from os.path import isdir, expanduser, sep
from sys import argv, stdout
from time import time_ns

from readchar import readchar
from colorama import init, Fore, Back, Cursor, Style
init()  # initialize colorama - for windows

scores_dir = ".mines_scores"
playing = True  # indicates when the game is over
board = []  # holds the board
"""
    in the board, a -1 means a mine, 
    a 0 means an empty cell with no mines around it a
    any other number just indicates how many mines are there around it
"""
display = []  # holds what's already revealed
"""
    same as the board but with
    -2 as a non-revealed cell
    '?' as a question mark 
"""
mines_percent = 15
try:
    rows, cols = int(argv[1]), int(argv[2])
    if rows < 5 or cols < 5:
        print("Smallest board is 5x5")
    if len(argv) > 3:
        mines_percent = int(argv[3])
        if 100 < mines_percent or mines_percent < 1:
            print(f"Mines percent cannot be {mines_percent}")
            exit()
except IndexError:
    print("Requires 2 arguments")
    print(f"Usage: {argv[0]} # # [%]")
    exit()
except ValueError:
    print("All arguments have to be integers")
    exit()

mines = int(rows * cols * mines_percent / 100)  # number of mines

if mines == 0:
    print("This is game has no mines and is therefore pointless")
    exit()
elif mines > rows * cols - 9:
    print("This game has too many mines")
    exit()

selected_cell = [0, 0]


def init_board():
    """
    initializes board as a row X cols array of 0s and display with -2s
    """
    global board, display
    for _ in range(rows):
        board += [[]]
        display += [[]]
        for __ in range(cols):
            board[-1] += [0]
            display[-1] += [-2]


def add_mines():
    """
    Add the mines to the board
    this function is called after the board has been initialized
    and the user selected theirs starting point
    """
    tmp = mines
    while tmp > 0:
        x, y = randint(0, cols - 1), randint(0, rows - 1)  # choose a random cell
        if selected_cell[0] - 1 <= y <= selected_cell[0] + 1 and \
                selected_cell[1] - 1 <= x <= selected_cell[1] + 1:
            continue  # do not add mines in the starting point and the cells around it
        if board[y][x] == -1:
            continue  # whoops! there's already a mine here
        board[y][x] = -1
        tmp -= 1


def add_numbers():
    """
    for each non-mine cell, count the mines around it and put that number in the cell
    """
    for y in range(rows):
        for x in range(cols):
            if board[y][x] == -1:
                continue
            local_mines = 0
            for a in range(y-1, y+2):
                for b in range(x-1, x+2):
                    if rows > a >= 0 and cols > b >= 0:  # make sure we don't go over the board's edges
                        if board[a][b] == -1:
                            local_mines += 1
            board[y][x] = local_mines


def print_board():
    print_game(board)


def pprint(*args, **kwargs):
    print(*args, **kwargs, end="")


def print_game(b=None):
    """
    prints the game's board
    :param b: what board to use - :var board or :var display there
    """
    if b is None:
        b = display
    system("clear || cls")  # start by clearing the console then
    pprint(Cursor.POS(1, 1))  # jump to position 1, 1 and start printing
    mines_already_used = 0
    for y in range(rows):
        for x in range(cols):
            cell = b[y][x]
            if cell == 0:
                pprint("·  ")
            elif cell == -1:
                pprint("*  ")
                mines_already_used += 1
            elif cell == -2:
                pprint("-  ")
            else:
                pprint(cell, " ")
        print()

    pprint(Cursor.POS(cols * 3 + 2, 1))  # jump to first line, 2 columns after the end of the board to
    pprint(Back.WHITE)
    if mines_already_used > mines:
        pprint(Fore.RED)
    elif mines_already_used == mines:
        pprint(Fore.GREEN)
    else:
        pprint(Fore.BLACK)

    pprint(mines_already_used, "/", mines)  # print the mines status

    print(Style.RESET_ALL, " ", Back.WHITE + Fore.BLACK + f"{selected_cell[0]}, {selected_cell[1]}")

    pprint(Style.RESET_ALL)

    pprint(Cursor.POS(selected_cell[1] * 3 + 1, selected_cell[0] + 1))  # put the cursor on the selected cell
    stdout.flush()


def reveal(y, x):
    """
    reveals selected 0 cell and it's surroundings recursively
    :param y: selected row
    :param x: selected column
    """
    display[y][x] = 0  # given cell is a 0
    for a in range(y - 1, y + 2):
        for b in range(x - 1, x + 2):
            if a == y and b == x:
                continue  # avoid infinite recursion on selected cell
            if rows > a >= 0 and cols > b >= 0 and \
                    board[a][b] != display[a][b]:
                # do not go over the board and do not try to revel an already revealed cell
                if board[a][b] == 0:
                    reveal(a, b)
                else:
                    display[a][b] = board[a][b]


def play(mode):
    global playing
    y, x = selected_cell
    if mode == 2:
        if display[y][x] == "?":
            display[y][x] = -2
        elif display[y][x] in [-1, -2]:
            display[y][x] = "?"
    elif mode == 1:
        if display[y][x] == -1:
            display[y][x] = -2
        elif display[y][x] in ["?", -2]:
            display[y][x] = -1
    elif mode == 0:
        cell = board[y][x]
        if cell == -1:
            print_board()
            print(Cursor.POS(0, rows))
            print(Fore.RED + "Boom! That was a mine")
            playing = False
        elif cell == 0:
            reveal(y, x)
        else:
            display[y][x] = cell


def get_input():
    pprint(Cursor.POS(selected_cell[1] * 3 + 1, selected_cell[0] + 1))
    stdout.flush()
    esc = False
    bracket = False
    while True:
        char = readchar()
        if char == '\x03':
            print(Cursor.POS(0, rows))
            print(Fore.LIGHTMAGENTA_EX + "Going already? :(")
            exit(0)
        elif char == '\x1b':
            esc = True
        elif esc and bracket:
            if char == 'A':
                if selected_cell[0] > 0:
                    selected_cell[0] -= 1
            elif char == 'B':
                if selected_cell[0] < rows - 1:
                    selected_cell[0] += 1
            elif char == 'D':
                if selected_cell[1] > 0:
                    selected_cell[1] -= 1
            elif char == 'C':
                if selected_cell[1] < cols - 1:
                    selected_cell[1] += 1
            else:
                print(Cursor.POS(0, rows))
                return None
            print_game()
            esc = bracket = False
        elif esc:
            if char == '[':
                bracket = True
            else:
                bracket = False
        elif char in "nf?":
            print(Cursor.POS(0, rows))
            return "nf?".index(char)
        else:
            print(Cursor.POS(0, rows))
            return None


def check_win():
    """
    checks if the user has won by going through every cell in the board and comparing it to the display
    :return: if the user won
    """
    for y1, y2 in zip(display, board):
        for cell1, cell2 in zip(y1, y2):
            if cell1 != cell2:
                return False
    return True


def game():
    global scores_dir
    """
    main function:
        initialize board and display
        prints the board
        gets an input for selected start point
        adds mines and numbers
        the while game is going, get a input and make a move
    """
    init_board()
    print_game()
    inp = get_input()
    while inp != 0:
        print(Fore.LIGHTRED_EX + "Invalid input" + Style.RESET_ALL)
        inp = get_input()
    add_mines()
    add_numbers()
    play(inp)
    start_time = time_ns()
    while playing:
        print_game()
        if check_win():
            print(Cursor.POS(0, rows) + Fore.GREEN)  # print under board in green
            end_time = time_ns()
            dur = end_time - start_time
            dur /= 1000000000
            print(f"You Won! and did it within {int(dur // 60)}:{int(dur) % 60}")
            name = input(f"{Fore.BLUE}Your Name (blank if you don't wanna save): {Fore.WHITE}")
            if name != "":
                home = expanduser("~")
                scores_dir = home + sep + scores_dir
                if not isdir(scores_dir):
                    mkdir(scores_dir)

                with open(f"{scores_dir}{sep}{rows}_{cols}_{mines_percent}", 'a') as score_file:
                    score_file.write(f"{int(dur // 60)}:{dur % 60} {name}\n")
            break
        inp = get_input()
        while inp is None:
            print(Fore.LIGHTRED_EX + "Invalid input" + Style.RESET_ALL)
            inp = get_input()
        play(inp)


game()


