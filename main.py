import time
import keyboard

from xkbgroup import XKeyboard
from parameters import RUS_CHARS, ENG_CHARS
from parameters import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS

buffer = []
ngrams_ru = []
ngrams_en = []

listener_enabled = True

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
    global listener_enabled

    initial_layout = get_layout()
    listener_enabled = False
    keyboard.send(SYS_SWITCH_KEY)
    listener_enabled = True

    for _ in range(20):
        time.sleep(0.05)
        layout = get_layout()

        if layout != initial_layout:
            time.sleep(0.3)
            return True

    return False


def auto_process(char):
    """ No comments. """
    global listener_enabled
    print('auto_process', char)

    if char in ASWITCH_KEYS:
        print('ASWITCH_KEYS', buffer)

        listener_enabled = False
        string = ''.join(buffer)
        initial_layout = get_layout()

        if not (initial_layout == 'us' and ngram_contain(string[:-1], ngrams_en) or
                initial_layout == 'ru' and ngram_contain(string[:-1], ngrams_ru)):
            return

        for _ in buffer:
            keyboard.send('backspace')

        switch_layout()
        keyboard_type(buffer, 0.01)
        keyboard.read_event()
        listener_enabled = True


def manual_process(char):
    """ No comments. """
    global listener_enabled
    print('manual_process', char)

    if char in MSWITCH_KEYS:
        listener_enabled = False

        for _ in buffer:
            keyboard.send('backspace')

        switch_layout()
        keyboard_type(buffer, 0.01)
        keyboard.read_event()
        listener_enabled = True


def update_buffer(char):
    """ No comments. """
    print('char =', char)

    if (char in RUS_CHARS + ENG_CHARS
            and len(buffer) >= 2
            and buffer[-1] == ' '):
        buffer.clear()

    if char in RUS_CHARS + ENG_CHARS:
        if keyboard.is_pressed('shift'):
            char = 'shift+' + char
        buffer.append(char)

    if char == 'space':
        buffer.append(' ')

    if char == 'backspace':
        if buffer:
            buffer.pop()

    if char in ('left', 'right', 'up', 'down', 'delete', 'enter'):
        buffer.clear()

    print(buffer)


def on_press(key):
    """ No comments. """
    update_buffer(key.name)
    manual_process(key.name)
    auto_process(key.name)


def main():
    """ No comments. """
    global listener_enabled
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_UP and listener_enabled:
            if event.name == 'f12':
                break
            listener_enabled = False
            on_press(event)
            listener_enabled = True


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

    import subprocess
    result = subprocess.run(
        ['ls', '-l'], capture_output=True, text=True).stdout
    print(result)

    main()
