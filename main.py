import time
import mouse
import keyboard
import parameters

from xkbgroup import XKeyboard
from parameters import RUS_CHARS, ENG_CHARS
from parameters import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS

buffer = []
ngrams_ru = []
ngrams_en = []

xkb = XKeyboard()


def load_ngrams(filenames):
    """ No comments. """
    result = []
    for filename in filenames:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f]
            result.extend(lines)
    return result


def ngram_contain(string, ngrams):
    """ Проверяет содержится ли строка string в списке n-грам ngrams. """
    string = string.lower()
    for ngram in ngrams:
        if ngram.startswith('*'):
            if string.endswith(ngram[1:]):
                return True
        elif ngram.endswith('*'):
            if string.startswith(ngram[:-1]):
                return True
        elif ngram in string:
            return True
    return False


def get_layout():
    """ No comments. """
    return xkb.group_symbol


def keyboard_type(text: list, delay: int = 0):
    """ Печатает переданный список нажатий клавиш. """
    for keys in text:
        keyboard.send(keys)
        time.sleep(delay)


def switch_layout():
    """ No comments. """
    keyboard.send(SYS_SWITCH_KEY)


def auto_process(char):
    """ No comments. """
    print('auto_process', char)

    if char in ASWITCH_KEYS:
        print('ASWITCH_KEYS', buffer)
        string = ''.join(buffer)
        initial_layout = get_layout()

        if not (initial_layout == 'us' and ngram_contain(string[:-1], ngrams_en) or
                initial_layout == 'ru' and ngram_contain(string[:-1], ngrams_ru)):
            return

        for _ in buffer:
            keyboard.send('backspace')

        switch_layout()
        keyboard_type(buffer)
        keyboard.read_event()


def manual_process(char):
    """ No comments. """
    print('manual_process', char)

    if char in MSWITCH_KEYS:

        for _ in buffer:
            keyboard.send('backspace')

        switch_layout()
        keyboard_type(buffer)
        keyboard.read_event()


def update_buffer(char):
    """ No comments. """
    print('char =', char)

    if (char in RUS_CHARS + ENG_CHARS
            and len(buffer) >= 2
            and buffer[-1] == ' '):
        buffer.clear()

    if char in RUS_CHARS + ENG_CHARS:
        if keyboard.is_pressed('ctrl'):
            return
        if keyboard.is_pressed('shift'):
            char = 'shift+' + char
        buffer.append(char)
        return

    if char == 'space':
        buffer.append(' ')
        return

    if char == 'backspace':
        if buffer:
            buffer.pop()
        return

    if (char not in RUS_CHARS + ENG_CHARS
            and char not in ASWITCH_KEYS + MSWITCH_KEYS
            and char not in ('ctrl+shift', 'ctrl', 'shift', 'space')):
        buffer.clear()

    print(buffer)


def on_press(key):
    """ No comments. """
    update_buffer(key.name)
    if parameters.MANUAL_ENABLED:
        manual_process(key.name)
    if parameters.AUTO_ENABLED:
        auto_process(key.name)


def on_mouse_click():
    buffer.clear()


def main():
    """ No comments. """
    mouse.on_button(on_mouse_click)
    while True:
        event = keyboard.read_event()
        if event.name == 'f12':
            break
        if event.event_type == keyboard.KEY_UP:
            on_press(event)


if __name__ == '__main__':
    ngrams_ru = load_ngrams((
        './data/nonexistent2gram-ru-tran.txt',
        './data/nonexistent3gram-ru-tran.txt',
        './data/nonexistent4gram-ru-tran.txt',
    ))
    ngrams_en = load_ngrams((
        './data/nonexistent2gram-en.txt',
        './data/nonexistent3gram-en.txt',
        './data/nonexistent4gram-en.txt',
    ))

    main()
