# The code below is a compressed version of maskpass found at:
# https://github.com/FuturisticGoo/maskpass

import sys
import termios
import tty

def askpass(prompt="Enter Password: ", mask="*"):
    char = b""
    password_input = b""
    count = 0

    print(prompt, end="", flush=True)

    def __posix_getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode()

    while True:
        char = __posix_getch()
        if char == b"\x03":
            # Ctrl-C Character
            raise KeyboardInterrupt
        elif char == b"\x1b":
            # Escape character
            password_input = b""
            break
        elif char == b"\r":
            break
        elif char in [b"\x08", b"\x7f"]:
            if count != 0:
                print("\b \b"*len(mask), end="", flush=True)
                count -= 1
            password_input = password_input[:-1]
        else:
            print(mask, end="", flush=True)
            if mask != "":
                count += 1
            password_input += char
    print(flush=True)
    return password_input.decode()