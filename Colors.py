GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESETCOLOR = '\033[39m'
RESETBGCOLOR = '\033[49m'
RESET = '\033[0m'
UNDERLINE = '\033[4m'
UNUNDERLINE = '\033[24m'
BOLD = '\033[1m'
UNBOLD = '\033[2m'


def background_color(r: int, g: int, b: int):
    print(f'\033[48;2;{r};{g};{b}m', end='')
