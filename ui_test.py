import getpass
import msvcrt
import os
CHARSETS_DIR = 'bin/charsets/'
USER = getpass.getuser()
COLORS = {
    'reset': '\033[0m',
    'highlight': '\033[47m',
}


def add_to_rows(rows: list, prefix: str = '', suffix: str = '') -> list:
    return [f'{prefix}{row}{suffix}' for row in rows]


#def colorize(text: str) -> (str, int):
#    compensation = 0
#    result = ''
#    while True:
#        delim_at = text.find('#')
#        if delim_at == -1:
#            result += text
#            break
#        code = text[delim_at+1:delim_at+7]
#        if text[delim_at+1] == '#':
#            color = COLORS['reset']
#            plain_text = text[:delim_at]
#            result += f'{plain_text}{color}'
#            compensation += len(color)
#            text = text[delim_at+2:]
#        elif text[delim_at+7] == '#':
#            r, g, b = int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16)
#            color = f'\033[38;2;{r};{g};{b}m'
#            plain_text = text[:delim_at]
#            result += f'{plain_text}{color}'
#            compensation += len(color)
#            text = text[delim_at+8:]
#    return result, compensation


class Charset:
    def __init__(self):
        self.symbols = None
        self.height = None

    def __getitem__(self, text: str) -> list:
        result_rows = ['' for _ in range(self.height)]
        for let in text:
            let = let.lower()
            if let not in self.symbols:
                continue
            for i, row in enumerate(self.symbols[let]):
                result_rows[i] += row
        return result_rows


def load_charset(filepath: str) -> Charset:
    file = open(filepath, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    new_charset = Charset()
    new_charset.symbols = {}
    entries = content.split('= NEXT =\n')
    for entry in entries:
        symbol_id = entry.find('symbol=')
        if symbol_id == -1: continue
        endl = entry.find('\n')
        symbol = entry[symbol_id+7:endl]
        char = entry[endl+1:].splitlines(keepends=False)
        height = len(char)
        new_charset.height = height if new_charset.height is None or height > new_charset.height else new_charset.height
        if symbol == 'space': symbol = ' '
        new_charset.symbols[symbol] = char
    return new_charset


class Menu:
    def __init__(self):
        self.sections = []
        self.actions = {}

    def AddRows(self, section: int, rows: list, padding: int = 0) -> None:
        while True:
            if section + 1 <= len(self.sections):
                break
            self.sections.append({'padding': 0, 'rows': []})

        self.sections[section]['padding'] = padding
        for row in rows:
            self.sections[section]['rows'].append(row)

    def Result(self) -> str:
        num_sections = len(self.sections)
        length = 0
        for section in self.sections:
            for row in section['rows']:
                row = row['text']
                row_length = len(row)
                length = row_length if row_length > length else length
        length += 2
        result = f'{Menu.GetHorizontalWall(length, True)}\n'
        for i, section in enumerate(self.sections):
            padding = section['padding']
            for row in section['rows']:
                row = row['text']
                result += f'{Menu.AddVerticalWalls(length, row, padding)}\n'
            if i + 1 != num_sections:
                result += f'{Menu.GetHorizontalDivider(length)}\n'
        result += f'{Menu.GetHorizontalWall(length, False)}\n'
        return result

    @staticmethod
    def GetHorizontalWall(length: int, ceiling: bool) -> str:
        left, right = '╔╗' if ceiling else '╚╝'
        middle = (length-2) * '═'
        return left + middle + COLORS['reset'] + right

    @staticmethod
    def AddVerticalWalls(length: int, text: str, padding: int = 0) -> str:
        length -= 2
        text = text[:length]
        padding_char = ('<', '^', '>')[padding]
        return f'║{text:{padding_char}{length}}║'

    @staticmethod
    def GetHorizontalDivider(length: int) -> str:
        return '╟' + (length-2) * '─' + '╢'


Charsets = {}
for file in os.listdir(CHARSETS_DIR):
    name, ext = os.path.splitext(file)
    Charsets[name] = load_charset(CHARSETS_DIR + file)

big_letters = Charsets['big']
small_letters = Charsets['small']


title1 = add_to_rows(big_letters['youtyoub'], prefix=' ', suffix=' ')
subtitle1 = add_to_rows(small_letters['choose an option below'], prefix=' ', suffix=' ')
menu = Menu()
menu.AddRows(0, [{'text': row} for row in title1], padding=1)
menu.AddRows(1, [{'text': row} for row in subtitle1], padding=0)
menu.AddRows(2, [{'text': ' [V]ideo', 'action': lambda: print('video')},
                 {'text': ' [P]laylist', 'action': lambda: print('playlist')},
                 {'text': ' [E]xit', 'action': lambda: exit(0)}], padding=0)
menu.AddRows(3, [{'text': 'Made by Matq on Discord '}], padding=2)

os.system('')
print(menu.Result())

while True:
    user_input = msvcrt.getch().lower()
    if user_input == b'\xe0':  # If the key is an extended key
        arrow_key = msvcrt.getch()

        if arrow_key == b'H':  # Up arrow key
            print("Up arrow key pressed")
        elif arrow_key == b'P':  # Down arrow key
            print("Down arrow key pressed")
        elif arrow_key == b'M':  # Right arrow key
            print("Right arrow key pressed")
        elif arrow_key == b'K':  # Left arrow key
            print("Left arrow key pressed")
        else:
            print("Unknown arrow key pressed")
    else:
        # Handle other characters
        if user_input == b'q':  # Example: Press 'q' to quit
            print("Quit key pressed")
            break
        else:
            if user_input in menu.actions:
                menu.actions[user_input]()
            print(f"Key pressed: {user_input}")

