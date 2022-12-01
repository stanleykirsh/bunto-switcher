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


def switch_layout():
    """ No comments. """
    initial_layout = get_layout()
    keyboard.send(SYS_SWITCH_KEY)

    for _ in range(50):
        time.sleep(0.04)
        layout = get_layout()

        if layout != initial_layout:
            time.sleep(0.3)
            return True

    return False


def suppress_listener(delay):
    """ No comments. """
    global listener_enabled
    listener_enabled = False

    def enable_listener():
        global listener_enabled
        listener_enabled = True

    keyboard.call_later(fn=enable_listener, args=(), delay=delay)


def auto_process(char):
    """ No comments. """
    print('auto_process', char)
    if char in ASWITCH_KEYS:
        print('ASWITCH_KEYS', buffer)
        string = ''.join(buffer)[:-1]
        initial_layout = get_layout()

        print('>>>char', char)
        print('initial_layout', initial_layout)
        print('ngram_contain(string, ngrams_en)', ngram_contain(string, ngrams_en))
        print('ngram_contain(string, ngrams_en)', ngram_contain(string, ngrams_ru))

        if not (initial_layout == 'us' and ngram_contain(string, ngrams_en) or
                initial_layout == 'ru' and ngram_contain(string, ngrams_ru)):
            return

        for _ in range(len(buffer) + 1):
            keyboard.send('backspace')

        switch_layout()
        keyboard.write(string + ' ')
        # buffer.clear()
        suppress_listener(0.02)


def manual_process(char):
    """ No comments. """
    print('manual_process', char)
    if char in MSWITCH_KEYS:
        string = ''.join(buffer)

        for _ in buffer:
            keyboard.send('backspace')

        switch_layout()
        keyboard.write(string)
        # buffer.clear()
        suppress_listener(0.02)


def update_buffer(char):
    """ No comments. """
    print('char =', char)

    if not listener_enabled:
        return

    if char in RUS_CHARS + ENG_CHARS and len(buffer) >= 2 and buffer[-1] == ' ':
        buffer.clear()
    if char in RUS_CHARS + ENG_CHARS:
        buffer.append(char)
    if char == 'space':
        buffer.append(' ')
    if char in ('left', 'right', 'up', 'down'):
        buffer.clear()

    print(buffer)


def on_press(key):
    """ No comments. """
    update_buffer(key.name)
    manual_process(key.name)
    #auto_process(key.name)


def main():
    """ No comments. """
    keyboard.on_release(callback=on_press)
    keyboard.wait('f12')


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
