import hashlib
from os import path
import random
import sys
import string
import tkinter as tk

prev_num = -1
path_string = ""
done = False
pristine = True

# defines mapping between points and coordinates; top left is 1, bottom right is 9, increasing to the right
LOCATIONS = {
    1: (75, 75),
    2: (150, 75),
    3: (225, 75),
    4: (75, 150),
    5: (150, 150),
    6: (225, 150),
    7: (75, 225),
    8: (150, 225),
    9: (225, 225)
}


def add_line(new_num):
    global path_string
    global prev_num

    if str(new_num) in path_string:
        return

    # draw a line from current to next if this is not first
    if path_string != "":
        canv.create_line(*LOCATIONS[prev_num], *LOCATIONS[new_num], width=3)
    
    # define a mapping for finding intermediate points passed through
    # note: (3, 1) will need to be sorted to (1, 3) to work
    EXTRA = {
        (1, 3): 2,
        (1, 7): 4,
        (1, 9): 5,
        (2, 8): 5,
        (3, 7): 5,
        (4, 6): 5,
        (3, 9): 6,
        (7, 9): 8
    }
    pair = tuple(sorted((prev_num, new_num)))

    add = ""
    if pair in EXTRA:
        extra_point = EXTRA[pair]
        add = "" if str(extra_point) in path_string else str(extra_point)
        px, py = LOCATIONS[extra_point]
        canv.create_oval(px - 10, py - 10, px + 10, py + 10, fill="black")

    # fill in clicked point
    px, py = LOCATIONS[new_num]
    canv.create_oval(px - 10, py - 10, px + 10, py + 10, fill="black")

    path_string += add + str(new_num)
    prev_num = new_num


def save():
    global done
    if done:
        return

    # write salt for hasher into file
    #FILE_NAME = path.dirname(sys.argv[0])
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

    password = special_char + cap_char + num_char + "".join([TOTAL[b & 0x3F] for b in hash_bytes])
    print(password)
    print(path_string)

    # put a text box on the screen with the password pasted in
    hash_text.pack()
    hash_text.delete("1.0", tk.END)
    hash_text.insert(tk.INSERT, password)
    hash_text.config(state=tk.DISABLED)

    done = True
    btn_submit["state"] = tk.DISABLED


# reset all input states
def reset():
    global done
    global pristine
    global path_string
    global prev_num

    pristine = True
    if done:
        hash_text.pack_forget()
        hash_text.config(state=tk.NORMAL)

    done = False
    path_string = ""
    prev_num = -1

    btn_submit["state"] = tk.NORMAL

    canv.delete("all")
    for i in range(3):
        for j in range(3):
            canv.create_oval(65 + i * 75, 65 + j * 75, 85 + i * 75, 85 + j * 75, fill="gray")


# get a click event on the canvas and find if it is pointing at a point
def process_click(event):
    if done:
        return

    x, y = event.x, event.y
    if 65 < y < 85:
        if 65 < x < 85:
            add_line(1)
        elif 140 < x < 160:
            add_line(2)
        elif 215 < x < 235:
            add_line(3)
    elif 140 < y < 160:
        if 65 < x < 85:
            add_line(4)
        elif 140 < x < 160:
            add_line(5)
        elif 215 < x < 235:
            add_line(6)
    elif 215 < y < 235:
        if 65 < x < 85:
            add_line(7)
        elif 140 < x < 160:
            add_line(8)
        elif 215 < x < 235:
            add_line(9)


root = tk.Tk()
root.geometry("300x450")

# define a canvas to draw the points on
canv = tk.Canvas(root, width=300, height=300)
canv.bind("<Button-1>", process_click)
canv.pack()

# draw the circles defining the 3x3 grid
for i in range(3):
    for j in range(3):
        canv.create_oval(65 + i * 75, 65 + j * 75, 85 + i * 75, 85 + j * 75, fill="gray")

btn_submit = tk.Button(root, text="Submit", command=save)
btn_submit.pack()

btn_reset = tk.Button(root, text="Reset", command=reset)
btn_reset.pack()

# this is a text field where the text password will appear
hash_text = tk.Text(root, width=23, height=1)

root.mainloop()
