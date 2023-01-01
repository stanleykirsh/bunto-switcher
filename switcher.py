from parameters import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS
from parameters import RUS_CHARS, ENG_CHARS
from keyboard.keyboard import Keyboard
from mouse.mouse import Mouse
from xkbgroup import XKeyboard
from gi.repository import Gtk, Gdk

import gi
import time
import parameters

gi.require_version("Gtk", "3.0")


class Switcher():
    """ No comments. """

    def __init__(self):
        """ No comments. """

        self.xkb = XKeyboard()
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.ngrams_ru = []
        self.ngrams_en = []

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.ngrams_ru = self.load_ngrams(('./data/ngrams-ru.txt',))
        self.ngrams_en = self.load_ngrams(('./data/ngrams-en.txt',))

    def load_ngrams(self, filenames):
        """ No comments. """
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def ngram_contain_continuous(self, string, ngrams):
        """ Проверяет содержится ли строка string в списке n-грам ngrams
        в процессе ввода слова до того как будет введен разделитель.
        """
        string = string.lower()
        for ngram in ngrams:
            if string == ngram:
                return True
        return False

    def ngram_contain_complete(self, string, ngrams):
        """ Проверяет содержится ли строка string в списке n-грам ngrams
        при вводе разделителя типа пробела и т.д.
        """
        string = string.lower()
        strlen = len(string)
        for ngram in reversed(ngrams):
            if ((strlen <= 5 and string == ngram) or
                    (strlen > 5 and string.startswith(ngram))):
                return True
        return False

    def get_layout(self):
        """ No comments. """
        return self.xkb.group_symbol

    def translit(self, string: str):
        """ No comments. """
        RU = str(RUS_CHARS+' ')
        US = str(ENG_CHARS+' ')
        initial_layout = self.get_layout()
        if initial_layout == 'ru':
            translited = ''.join(RU[US.find(s)] for s in string)
            translited = ''.join(US[RU.find(s)] for s in translited)
        if initial_layout == 'us':
            translited = ''.join(RU[US.find(s)] for s in string)
        return translited

    def keyboard_type(self, text: list, delay: int = 0):
        """ Печатает переданный список нажатий клавиш. """
        for keys in text:
            self.keyboard.send(keys)
            time.sleep(delay)

    def switch_layout(self):
        """ No comments. """
        self.keyboard.send(SYS_SWITCH_KEY)

    def auto_process(self, char):
        """ No comments. """
        #print('auto_process', char)

        if char in ASWITCH_KEYS:
            #print('ASWITCH_KEYS', self.buffer)
            initial_layout = self.get_layout()
            string = ''.join(self.buffer).replace('shift+', '').strip()

            if not (initial_layout == 'ru' and self.ngram_contain_complete(string, self.ngrams_en) or
                    initial_layout == 'us' and self.ngram_contain_complete(string, self.ngrams_ru)):
                return

            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)
            # time.sleep(0.2)

            for _ in self.buffer:
                self.keyboard.send('backspace')
            self.keyboard.send('ctrl+v')
            self.keyboard.syn()
            time.sleep(0.2)

            self.switch_layout()
            # self.keyboard_type(text=self.buffer)
            self.keyboard.syn()

    def manual_process(self, char):
        """ No comments. """
        # print('manual_process', char)

        if char in MSWITCH_KEYS:
            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)
            # time.sleep(0.2)

            for _ in self.buffer:
                self.keyboard.send('backspace')
            self.keyboard.send('ctrl+v')
            self.keyboard.syn()
            time.sleep(0.25)

            self.switch_layout()
            # self.keyboard_type(text=self.buffer)
            self.keyboard.syn()

    def update_buffer(self, char):
        """ No comments. """
        # print('char =', char)

        if (char in RUS_CHARS + ENG_CHARS
                and len(self.buffer) >= 2
                and self.buffer[-1] == ' '):
            self.buffer.clear()

        if char in RUS_CHARS + ENG_CHARS:
            if self.keyboard.is_pressed('ctrl'):
                return
            if self.keyboard.is_pressed('shift'):
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

        # print(self.buffer)

    def on_mouse_click(self, event):
        print('on_mouse_click')
        self.buffer.clear()

    def on_key_pressed(self, event):
        """ No comments. """
        # print('on_key_pressed =', event.key_char)
        if event.type == 'up':
            key = event.key_char
            self.update_buffer(key)
            if parameters.MANUAL_ENABLED:
                self.manual_process(key)
            if parameters.AUTO_ENABLED:
                self.auto_process(key)

    def start(self):
        """ No comments. """
        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.on_key_pressed)
