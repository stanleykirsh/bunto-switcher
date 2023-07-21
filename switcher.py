from gi.repository import Gtk, Gdk
from settings import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS
from settings import RUS_CHARS, ENG_CHARS
from keyboard.keyboard import Keyboard
from mouse.mouse import Mouse
from xkbgroup import XKeyboard

import os
import time
import settings

import gi
gi.require_version('Gtk', '3.0')


class Switcher(Gtk.Window):
    """ No comments. """

    _SWITCH_DELAY = 0.2  # 0.5 sec

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

        string = string.lower()
        for ngram in ngrams:
            if ngram in string:
                return True
        return False

    def layout_prob(self, string: str):
        """ No comments. """

        string = string.lower()

        prob_ru = 0
        for ngram in self.ngrams_ru:
            if ngram in string:
                prob_ru += 1

        prob_en = 0
        for ngram in self.ngrams_en:
            if ngram in string:
                prob_en += 1

        print(prob_ru, prob_en)
        if prob_ru > prob_en:
            return 'ru'
        if prob_ru < prob_en:
            return 'us'
        if prob_ru == prob_en:
            return ''

    def get_layout(self):
        """ No comments. """

        return self.xkb.group_symbol

    def char_upper(self, char: str):
        """ No comments. """

        charid = ENG_CHARS.find(char) + 47
        if charid < len(ENG_CHARS):
            return ENG_CHARS[charid]
        else:
            return char

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

    def switch_required(self):
        """ No comments. """

        initial_layout = self.get_layout()
        string = ''.join(self.buffer).replace('shift+', '').strip()
        string = ' ' + string  # если первое слово в строке, то добавялем впереди пробел

        probability = self.layout_prob(string)
        if ((probability == 'ru' and initial_layout == 'us')
                or (probability == 'us' and initial_layout == 'ru')):
            return True

        return False

    def switch_layout(self):
        """ No comments. """

        self.keyboard.send(SYS_SWITCH_KEY)

    def auto_process(self, char: str):
        """ No comments. """

        # print('auto_process')
        if char in ASWITCH_KEYS:
            print('ASWITCH_KEYS')

            if not self.switch_required():
                return

            if settings.SWITCH_TWOCAPS:
                self.lower_leadings()

            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)

            for _ in self.buffer:
                self.keyboard.send('backspace')

            self.keyboard.send('ctrl+v')
            # self.clipboard.clear()

            # перед переключением раскладки даем время оболочке обработать все [виртуально] нажатые клавиши
            # потому что если это сделать сразу то оболочка пытается одновременно выводить текст и переключать раскладку
            # и в результате зависает
            time.sleep(self._SWITCH_DELAY)
            self.switch_layout()
            # self.keyboard.write(text=self.buffer)

    def manual_process(self, char: str):
        """ No comments. """

        if char in MSWITCH_KEYS:

            if settings.SWITCH_TWOCAPS:
                self.lower_leadings()

            translited = self.translit(''.join(self.buffer))
            self.clipboard.set_text(translited, -1)

            for _ in self.buffer:
                self.keyboard.send('backspace')

            self.keyboard.send('ctrl+v')
            # self.clipboard.clear()

            # перед переключением раскладки даем время оболочке обработать все [виртуально] нажатые клавиши
            # потому что если это сделать сразу то оболочка пытается одновременно выводить текст и переключать раскладку
            # и в результате зависает
            time.sleep(self._SWITCH_DELAY)
            self.switch_layout()
            # self.keyboard.write(text=self.buffer)

    def leading_caps_process(self, char: str):
        """ No comments. """

        # исправляем капсы только при инициализации ручного или автоматического переключения раскладки
        # если зашли сюда НЕ по триггеру ручного или автоматического переключения, то выходим
        # капсы исправлятся в процедуре переключения
        if char not in ASWITCH_KEYS + MSWITCH_KEYS:
            return

        # TBD
        if not self.is_lower_leadings():
            return

        # если требуется переключение раскладки, то выходим отсюда
        # капсы исправлятся в процедуре переключения
        if self.switch_required():
            return

        self.lower_leadings()
        string = ''.join(self.buffer)
        initial_layout = self.get_layout()

        if initial_layout == 'ru':
            RU = str(RUS_CHARS+' ')
            US = str(ENG_CHARS+' ')
            string = ''.join(RU[US.find(s)] for s in string)

        self.clipboard.set_text(string, -1)

        for _ in self.buffer:
            self.keyboard.send('backspace')

        self.keyboard.send('ctrl+v')

    def is_lower_leadings(self):
        """ No comments. """

        string = ''.join(self.buffer)

        if (True
            and len(string) >= 2
            and string[0:2].isupper()
            and not string[2:].isupper()
            and not string.isupper()
            ):
            return True

        return False

    def lower_leadings(self):
        """ No comments. """

        if self.is_lower_leadings():
            string = ''.join(self.buffer)
            self.buffer = list(string[0] + string[1:].lower())

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
                char = self.char_upper(char)
            if self.keyboard.is_caps_locked():
                char = self.char_upper(char)
            self.buffer.append(char)
            return

        if char == 'space':
            self.buffer.append(' ')
            return

        if char == 'backspace':
            if self.buffer:
                self.buffer.pop()
            return

        if (char not in RUS_CHARS + ENG_CHARS
                and char not in ASWITCH_KEYS + MSWITCH_KEYS
                and char not in ('ctrl+shift', 'ctrl', 'shift', 'space', 'caps lock')):
            self.buffer.clear()

    def on_mouse_click(self, event):
        """ No comments. """

        print('on_mouse_click')
        self.buffer.clear()

    def on_key_pressed(self, event):
        """ No comments. """

        key = event.key_char

        if event.type == 'down':
            self.update_buffer(key)

        if event.type == 'up':
            if settings.SWITCH_TWOCAPS:
                self.leading_caps_process(key)
            if settings.SWITCH_MANUAL:
                self.manual_process(key)
            if settings.SWITCH_AUTO:
                self.auto_process(key)

    def start(self):
        """ No comments. """

        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.on_key_pressed)
