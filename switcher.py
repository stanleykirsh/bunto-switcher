from gi.repository import Gtk, Gdk
from parameters import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS
from parameters import RUS_CHARS, ENG_CHARS
from keyboard.keyboard import Keyboard
from mouse.mouse import Mouse
from xkbgroup import XKeyboard

import os
import time
import parameters

import gi
gi.require_version('Gtk', '3.0')


class Switcher(Gtk.Window):
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

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',))
        self.ngrams_en = self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',))

    def load_ngrams(self, filenames):
        """ No comments. """
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def ngram_contain(self, string: str, ngrams: list):
        """ Проверяет содержит ли строка string хотя бы одну из n-грам ngrams.
        Эта функция предназначена для проверки при вводе разделителя типа пробела и т.д.
        """
        for ngram in ngrams:
            if ngram in string:
                return True
        return False

    '''
    def ngram_contain(self, string: str, ngrams: list):
        """ Проверяет содержится ли строка string в списке n-грам ngrams
        при вводе разделителя типа пробела и т.д.
        """
        strlen = len(string)
        string = string.lower()
        for ngram in reversed(ngrams):
            if ((strlen <= 5 and string == ngram) or
                    (strlen > 5 and len(ngram) >= 5 and string.startswith(ngram))):
                print(string, ngram)
                return True
        return False
    '''

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

    def switch_layout(self):
        """ No comments. """
        self.keyboard.send(SYS_SWITCH_KEY)

    def auto_process(self, char: str):
        """ No comments. """
        print('auto_process')

        if char in ASWITCH_KEYS:
            print('ASWITCH_KEYS')
            initial_layout = self.get_layout()
            string = ''.join(self.buffer).replace('shift+', '').strip()
            string = ' ' + string  # если первое слово в строке, то добавялем впереди пробел

            if not (
                    initial_layout == 'ru' and self.ngram_contain(string, self.ngrams_en) or
                    initial_layout == 'us' and self.ngram_contain(string, self.ngrams_ru)):
                return

            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)

            for _ in self.buffer:
                self.keyboard.send('backspace')

            self.keyboard.send('ctrl+v')

            time.sleep(0.2)
            self.switch_layout()
            # self.keyboard.write(text=self.buffer)

    def manual_process(self, char: str):
        """ No comments. """

        if char in MSWITCH_KEYS:
            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)

            for _ in self.buffer:
                self.keyboard.send('backspace')

            self.keyboard.send('ctrl+v')

            time.sleep(0.2)
            self.switch_layout()
            # self.keyboard.write(text=self.buffer)

    def update_buffer(self, char: str):
        """ No comments. """

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

    def on_mouse_click(self, event):
        print('on_mouse_click')
        self.buffer.clear()

    def on_key_pressed(self, event):
        """ No comments. """
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
