from os import system
from time import sleep
from sys import stdout
from datetime import datetime
import msvcrt

ESC_ONE = '\033[%sm'
ESC_RGB_F = '\033[38;2;%s;%s;%sm'
ESC_RGB_B = '\033[48;2;%s;%s;%sm'

MODS = {
    'reset': ESC_ONE % 0,
    'bold': ESC_ONE % 1,  # bold the text
    'faint': ESC_ONE % 2,  # faint the text
    'dbf': ESC_ONE % 22,  # default bold / faint

    'italic': ESC_ONE % 3,  # italic the text
    'unitalic': ESC_ONE % 23,  # remove italic

    'underline': ESC_ONE % 4,  # underline the text
    'doublylined': ESC_ONE % 21,  # double underline
    'dul': ESC_ONE % 24,  # default underline

    'invert': ESC_ONE % 7,  # invert colors
    'uninvert': ESC_ONE % 27,  # remove inverted

    'strikethrough': ESC_ONE % 9,  # line through the text
    'unstrikethrough': ESC_ONE % 29,  # remove strikethrough

    'dfc': ESC_ONE % 39,  # default foreground color
    'dbc': ESC_ONE % 49,  # default background color

    'frame': ESC_ONE % 51,  # frame the text
    'encircle': ESC_ONE % 52,  # encircle the text
    'dfe': ESC_ONE % 54,  # default frame / encircle
}

INFORMATION = {
    'reset': 'works everywhere',
    'bold': 'works everywhere',
    'faint': 'doesn\'t work on windows console',
    'dbf': 'works everywhere',

    'italic': 'doesn\'t work on windows console',
    'unitalic': 'doesn\'t work on windows console',

    'underline': 'works everywhere',
    'doublylined': 'doesn\'t work on windows console',
    'dul': 'works everywhere',

    'invert': 'works everywhere',
    'uninvert': 'works everywhere',

    'strikethrough': 'works everywhere',
    'unstrikethrough': 'works everywhere',

    'dfc': 'works everywhere',
    'dbc': 'works everywhere',

    'frame': 'doesn\'t work on windows console',
    'encircle': 'doesn\'t work on windows console',
    'dfe': 'doesn\'t work on windows console',
}


def colorf(r, g, b) -> str:
    return ESC_RGB_F % (r, g, b)


def colorb(r, g, b) -> str:
    return ESC_RGB_B % (r, g, b)


def get_colors_from_code(indice: str):
    if len(indice) != 7 or not all(c in '0123456789abcdef' for c in indice[1:7].lower()):
        return None

    return int(indice[1:3], 16), int(indice[3:5], 16), int(indice[5:7], 16)


def parse_insets(text: str) -> tuple:
    mods = []
    new_text = ''
    while True:
        delim_at = text.find('#')
        if delim_at == -1 or len(text) - 1 == delim_at:  # no codes found
            new_text += text[:delim_at]
            break

        if color := get_colors_from_code(text[delim_at:delim_at + 7]):
            mods.append((delim_at, colorf(*color)))
            new_text += text[:delim_at]
            skip_chars = 7
        else:
            new_text += text[:delim_at]
            spec_char = text[delim_at + 1]
            if spec_char == '#':
                new_text += '#'  # just hashtag
            elif spec_char == 'r':
                mods.append((delim_at, MODS['reset']))
            skip_chars = 2

        text = text[delim_at + skip_chars:]
    return new_text, mods


def inset(mod_text: tuple) -> str:
    text, mods = mod_text
    new_text = ''
    for mod_idx, mod in mods:
        if mod_idx < -1: continue
        if mod_idx == -1: mod_idx = len(text)
        new_text += text[:mod_idx]
        text = text[mod_idx:]
        new_text += mod
    new_text += text
    return new_text


def generate_rainbow_inset(length: int, offset: int = 0) -> list:
    rainbow = [
        colorf(*get_colors_from_code('#ff0000')),
        colorf(*get_colors_from_code('#ffA500')),
        colorf(*get_colors_from_code('#ffff00')),
        colorf(*get_colors_from_code('#00ff00')),
        colorf(*get_colors_from_code('#00ffff')),
        colorf(*get_colors_from_code('#0000ff')),
        colorf(*get_colors_from_code('#ff00ff')),
    ]
    num_colors = len(rainbow)
    return [(int(i != 0), rainbow[(i + offset) % num_colors]) for i in range(length)]


def main():
    system('')
    stdout.write('\033[?25l')
    stdout.flush()

    raw_text = '#ff0000Red #ffffAAColor#r Yeees!'
    inset_text = parse_insets(raw_text)
    new_text = inset(inset_text)
    test3_text = 'Ayo what is happening wtfffffffffffff'

    print('Test1')
    print(f'{raw_text}')
    print(f'{inset_text}')
    print(f'{new_text}\n{new_text.__repr__()}')
    print()

    print('Test2')
    print(inset(('Hallooooooooooooooooooo', [(10, colorf(255, 0, 0)), (5, colorf(0, 0, 255)), (-1, MODS['reset'])])))
    print()

    print('Test3')
    for i in range(7):
        print(inset((test3_text, [*generate_rainbow_inset(len(test3_text), i), (-1, MODS['reset'])])))
    print()

    print('Test4')
    test4_text = 'Weeeeeee'
    test4_string = inset((test4_text, generate_rainbow_inset(len(test4_text))))
    test4_length = len(test4_string)
    print(test4_string, end='')
    for i in range(10):
        sleep(0.01)
        test4_string = inset((test4_text, generate_rainbow_inset(len(test4_text), i+1)))
        print('\b' * test4_length, test4_string, sep='', end='', flush=True)
        test4_length = len(test4_string)
    print(MODS['reset'])
    print()

    print('Test5')
    options = [
        'Download video',
        'Download playlist of videos',
        'Leave program',
    ]
    selected = 0
    while True:
        for i in range(len(options)):
            if i == selected:
                inset_text = options[i], [(0, ESC_RGB_B % (128, 128, 128)), (-1, MODS["reset"])]
                compensation = sum([len(mod[1]) for mod in inset_text[1]])
                stdout.write(f'║ {inset(inset_text):<{40+compensation}} ║\n')
            else:
                stdout.write(f'║ {options[i]:<40} ║\n')

        stdout.flush()

        user_input = msvcrt.getch().lower()
        if user_input == b'\r':
            break
        elif user_input == b'\xe0':  # If the key is an extended key
            arrow_key = msvcrt.getch()

            if arrow_key == b'H':  # Up arrow key
                selected = selected - 1 if selected > 0 else selected
            elif arrow_key == b'P':  # Down arrow key
                selected = selected + 1 if selected < 2 else selected
        else:
            if user_input == b'w':
                selected = selected - 1 if selected > 0 else selected
            elif user_input == b's':
                selected = selected + 1 if selected < 2 else selected

        stdout.write('\033[3A')
    print(f'Selected option was: {options[selected]}')
    print()

    print('Test6')
    options = [
        'Become youtuber',
        'Become doctor',
        'Become hamburger',
    ]
    selected = 0
    offset = 0
    while True:
        for i in range(len(options)):
            inset_text = options[i], generate_rainbow_inset(len(options[i]), offset+i)
            if i == selected:
                inset_text[1].insert(0, (0, ESC_RGB_B % (128, 128, 128)))
            inset_text[1].append((-1, MODS['reset']))
            compensation = sum([len(mod[1]) for mod in inset_text[1]])
            stdout.write(f'║ {inset(inset_text):<{40 + compensation}} ║\n')

        stdout.flush()

        began = datetime.now()
        while True:
            if (datetime.now() - began).microseconds >= 1000 * 100 or msvcrt.kbhit():  # 100 miliseconds
                offset += 1
                break

        if msvcrt.kbhit():
            user_input = msvcrt.getch().lower()
            if user_input == b'\r':
                break
            elif user_input == b'\xe0':  # If the key is an extended key
                arrow_key = msvcrt.getch()

                if arrow_key == b'H':  # Up arrow key
                    selected = selected - 1 if selected > 0 else selected
                elif arrow_key == b'P':  # Down arrow key
                    selected = selected + 1 if selected < 2 else selected
            else:
                if user_input == b'w':
                    selected = selected - 1 if selected > 0 else selected
                elif user_input == b's':
                    selected = selected + 1 if selected < 2 else selected

        stdout.write('\033[3A')
    print(f'Selected option was: {options[selected]}')
    print()

    system('pause')


if __name__ == '__main__':
    main()
