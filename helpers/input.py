import sys
import getpass
import termios
import tty


def input_with_mask(prompt="Enter password: "):
    print(prompt, end="", flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        password = ""
        while True:
            char = sys.stdin.read(1)
            if char == "\n":
                break
            elif char == "\x7f":  # Handle backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
            else:
                password += char
                sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print()  # To move to the next line after input is complete
    return password
