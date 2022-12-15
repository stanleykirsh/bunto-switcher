import time
import mouse
import keyboard
import parameters

from xkbgroup import XKeyboard
from parameters import RUS_CHARS, ENG_CHARS
from parameters import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS


class Switcher():
    """ No comments. """
    xkb = XKeyboard()

    buffer = []
    ngrams_ru = []
    ngrams_en = []
    supressed = False

    def __init__(self):
        """ No comments. """
        self.ngrams_ru = self.load_ngrams((
            './data/triggers-ru-tran.txt',
            './data/nonexistent4gram-ru-tran.txt',
            './data/nonexistent3gram-ru-tran.txt',
            './data/nonexistent2gram-ru-tran.txt',
        ))
        self.ngrams_en = self.load_ngrams((
            './data/triggers-en.txt',
            './data/nonexistent4gram-en.txt',
            './data/nonexistent3gram-en.txt',
            './data/nonexistent2gram-en.txt',
        ))

    def load_ngrams(self, filenames):
        """ No comments. """
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def ngram_contain(self, string, ngrams):
        """ Проверяет содержится ли строка string в списке n-грам ngrams. """
        string = string.lower()
        for ngram in ngrams:
            if ngram in string:
                return True
            elif ngram.startswith('*'):
                if string.startswith(ngram[1:]):
                    return True
            elif ngram.endswith('*'):
                if string.endswith(ngram[:-1]):
                    return True
        return False

    def get_layout(self):
        """ No comments. """
        return self.xkb.group_symbol

    def keyboard_type(self, text: list, delay: int = 0):
        """ Печатает переданный список нажатий клавиш. """
        for keys in text:
            keyboard.send(keys)
            time.sleep(delay)

    def switch_layout(self):
        """ No comments. """
        keyboard.send(SYS_SWITCH_KEY)

    def auto_process(self, char):
        """ No comments. """
        print('auto_process', char)

        if char in ASWITCH_KEYS:
            print('ASWITCH_KEYS', self.buffer)
            string = ''.join(self.buffer)
            initial_layout = self.get_layout()

            if not (initial_layout == 'us' and self.ngram_contain(string[:-1], self.ngrams_en) or
                    initial_layout == 'ru' and self.ngram_contain(string[:-1], self.ngrams_ru)):
                return

            for _ in self.buffer:
                keyboard.send('backspace')

            self.switch_layout()
            self.keyboard_type(
                text=self.buffer, delay=0.01)

    def manual_process(self, char):
        """ No comments. """
        print('manual_process', char)

        if char in MSWITCH_KEYS:
            for _ in self.buffer:
                keyboard.send('backspace')

            self.switch_layout()
            self.keyboard_type(
                text=self.buffer, delay=0.01)

    def update_buffer(self, char):
        """ No comments. """
        print('char =', char)

        if (char in RUS_CHARS + ENG_CHARS
                and len(self.buffer) >= 2
                and self.buffer[-1] == ' '):
            self.buffer.clear()

        if char in RUS_CHARS + ENG_CHARS:
            if keyboard.is_pressed('ctrl'):
                return
            if keyboard.is_pressed('shift'):
                char = 'shift+' + char
            self.buffer.append(char)
            return

        if char == 'space':
            self.buffer.append(' ')
            return

        # if char == 'backspace':
        #    if self.buffer:
        #        self.buffer.pop()
        #    return

        if (char not in RUS_CHARS + ENG_CHARS
                and char not in ASWITCH_KEYS + MSWITCH_KEYS
                and char not in ('ctrl+shift', 'ctrl', 'shift', 'space')):
            self.buffer.clear()

        print(self.buffer)

    def on_mouse_click(self):
        self.buffer.clear()

    def on_release(self, key):
        """ No comments. """
        if self.supressed:
            return
        self.lock_listener()
        self.update_buffer(key.name)
        if parameters.MANUAL_ENABLED:
            self.manual_process(key.name)
        if parameters.AUTO_ENABLED:
            self.auto_process(key.name)
        self.unlock_listener()

    def lock_listener(self):
        self.supressed = True

    def unlock_listener(self):
        def _unlock():
            self.supressed = False
        keyboard.call_later(fn=_unlock, delay=0.01)

    def main(self):
        """ No comments. """
        mouse.on_button(self.on_mouse_click)
        keyboard.on_release(self.on_release)

    def start(self):
        """ No comments. """
        self.main()
