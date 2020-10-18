import hashlib
from os import path
import random
import sys
import string

grid = [[" " for x in range(13)] for y in range(7)]
grid[0][0] = "1"
grid[0][6] = "2"
grid[0][12] = "3"
grid[3][0] = "4"
grid[3][6] = "5"
grid[3][12] = "6"
grid[6][0] = "7"
grid[6][6] = "8"
grid[6][12] = "9"

prev_num = -1
path_string = ""


def get_grid_position(num):
    row = (num - 1) // 3
    col = (num - 1) % 3
    return (col * 6, row * 3)


def add_line(new_num):
    global path_string
    global prev_num

    next_pos = get_grid_position(new_num)

    # draw a line from current to next if this is not first
    if path_string != "":
        prev_pos = get_grid_position(prev_num)

        dx = next_pos[0] - prev_pos[0]
        dy = next_pos[1] - prev_pos[1]

        num_draw = min(abs(dx), abs(dy)) if (dx != 0 and dy != 0) else max(abs(dx) // 2, abs(dy))
        for i in range(num_draw):
            frac = i / num_draw
            x = round(prev_pos[0] + frac * dx)
            y = round(prev_pos[1] + frac * dy)
            grid[y][x] = "*"

    add = ""
    extra = {
        (1, 3): 2,
        (1, 7): 4,
        (1, 9): 5,
        (3, 7): 5,
        (3, 9): 6,
        (7, 9): 8
    }
    pair = tuple(sorted((prev_num, new_num)))
    if pair in extra:
        add += str(extra[pair])
    path_string += add + str(new_num)
    prev_num = new_num

    grid[next_pos[1]][next_pos[0]] = "*"


def draw_grid():
    # oh god why did i do this in one line
    print("\n" + "\n".join(["".join([ch if (ch in "123456789") else ("\033[94m" + ch + "\033[0m") for ch in row]) for row in grid]) + "\n")


print("Welcome to Pattword")

while True:
    draw_grid()
    inp = input("Enter a number (1-9). q to quit: ")
    if inp == "q":
        break

    if (not inp.isdigit()) or (1 > int(inp) > 9) or (inp in path_string):
        print("Invalid input.")
    else:
        add_line(int(inp))

print(path_string)

FILE_NAME = "super_secret_seed" # TODO change maybe; idea:    path.dirname(sys.argv[0])
if path.exists(FILE_NAME):
    salt = open(FILE_NAME, "r").read()
else:
    random.seed(None)
    salt = "".join([hex(random.randint(0, 15)).lstrip("0x") for i in range(random.randint(10, 30))])
    open(FILE_NAME, "w").write(salt)

SPECIAL = "!@#$%^&?()[]{}/\\"
hash_bytes = hashlib.sha1((salt + path_string).encode("utf-8")).digest()

# would like at least one special character, one capital letter, one number
special_char = SPECIAL[hash_bytes[0] >> 4]
cap_char = string.ascii_uppercase[hash_bytes[0] & 0xF]
num_char = string.digits[hash_bytes[1] & 0x7]

TOTAL = string.ascii_letters + string.digits + SPECIAL

print(special_char + cap_char + num_char + "".join([TOTAL[b & 0x3F] for b in hash_bytes]))
