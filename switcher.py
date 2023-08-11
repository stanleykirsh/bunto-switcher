from mouse.mouse import Mouse
from keyboard.keyboard import Keyboard
from settings import SYS_SWITCH_KEY, ASWITCH_KEYS, MSWITCH_KEYS
from gi.repository import Gtk, Gdk

import os
import time
import settings
import subprocess

import gi
gi.require_version('Gtk', '3.0')


class Switcher(Gtk.Window):
    """"""

    # перед переключением раскладки даем время оболочке обработать все [виртуально] нажатые клавиши
    # потому что если это сделать сразу то оболочка пытается одновременно выводить текст и переключать раскладку
    # и в результате зависает
    # для X11:      0.5 sec
    # для Wayland:  0.0 sec
    _SWITCH_DELAY = 0.0

    _RUS_CHARS = """ё1234567890-=йцукенгшщзхъфывапролджэ\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
    _ENG_CHARS = """`1234567890-=qwertyuiop[]asdfghjkl;'\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

    def __init__(self):
        """"""
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.ngrams_ru = []
        self.ngrams_en = []

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',))
        self.ngrams_en = self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',))

        self.username = os.environ['SUDO_USER']
        self.initial_layout = self.get_layout()

    def load_ngrams(self, filenames):
        """"""
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def layout_probability(self, string: str):
        """"""
        STRIP_US = ''',./<>?`~!@#$%^&*()_-=+|[]{};:'"'''
        STRIP_RU = '''@#$^&/?'''

        string = string.lower()
        for s in STRIP_US + STRIP_RU:
            string = string.replace(s, ' ')

        print(f'={string}=')

        if string in settings.IGNORE_WORDS.split('|'):
            return ''

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
        """"""
        # это работало в X11
        # print('get_layout', self.xkb.group_symbol)
        # return self.xkb.group_symbol
        # это по идее должно работать в X11 + Wayland
        get_mru_sources = f'sudo -u {self.username} gsettings get org.gnome.desktop.input-sources mru-sources'.split()
        result = subprocess.run(get_mru_sources, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8')[10:12]
        self.initial_layout = result
        return result

    def char_upper(self, char: str):
        """"""
        charid = self._ENG_CHARS.find(char) + 47
        if charid < len(self._ENG_CHARS):
            return self._ENG_CHARS[charid]
        else:
            return char

    def translit(self, string: str):
        """"""
        RU = str(self._RUS_CHARS+' ')
        US = str(self._ENG_CHARS+' ')

        if self.initial_layout == 'ru':
            translited = ''.join(RU[US.find(s)] for s in string)
            translited = ''.join(US[RU.find(s)] for s in translited)
        if self.initial_layout == 'us':
            translited = ''.join(RU[US.find(s)] for s in string)
        return translited

    def kb_switch_required(self):
        """"""
        string = ''.join(self.buffer)
        string = string.replace('shift+', '')
        string = string.replace('space', ' ')
        string = string.replace('tab', ' ')
        probability = self.layout_probability(string)
        if ((probability == 'ru' and self.initial_layout == 'us')
                or (probability == 'us' and self.initial_layout == 'ru')):
            return True
        return False

    def kb_switch_layout(self):
        """"""
        self.keyboard.send(SYS_SWITCH_KEY)

    def kb_auto_process(self, char: str):
        """"""
        if char not in ASWITCH_KEYS:
            return

        if not self.kb_switch_required():
            return

        self.delete_last_word(2 if self.buffer[-1] in ('enter') else 1)

        string = ''.join(self.buffer[:-1])
        string = self.translit(string)
        string = string + {'space': ' ', 'tab': '\t',
                           'enter': '\r\n'}[self.buffer[-1]]

        self.clipboard.set_text(string, -1)
        self.keyboard.send('ctrl+v')
        self.kb_switch_layout()
        time.sleep(0.05)
        self.get_layout()

    def kb_manual_process(self, char: str):
        """"""
        if char not in MSWITCH_KEYS:
            return

        self.delete_last_word(2 if self.buffer[-1] in ('enter') else 1)

        string = ''.join(self.buffer[:-1])
        string = self.translit(string)
        string = string + {'space': ' ', 'tab': '\t',
                           'enter': '\r\n'}[self.buffer[-1]]

        self.clipboard.set_text(string, -1)
        self.keyboard.send('ctrl+v')
        self.kb_switch_layout()
        time.sleep(0.05)
        self.get_layout()

    def caps_auto_process(self, char: str):
        """"""
        # исправляем капсы только при инициализации ручного или автоматического переключения раскладки
        # если зашли сюда НЕ по триггеру ручного или автоматического переключения, то выходим
        # капсы исправлятся в процедуре переключения
        if char not in ASWITCH_KEYS + MSWITCH_KEYS:
            return

        # если в буфере первые два символа не капсом,то выходим
        if not self.is_upper_leadings():
            return

        ###############################
        string = ''.join(self.buffer[:-1]).lower()

        if self.initial_layout == 'ru':
            RU = str(self._RUS_CHARS+' ')
            US = str(self._ENG_CHARS+' ')
            string = ''.join(RU[US.find(s)] for s in string)

        self.buffer = list(string) + [self.buffer[-1]]
        ################################

        # ######################
        if (self.kb_switch_required() and char in ASWITCH_KEYS):
            return

        if char in MSWITCH_KEYS:
            return

        # string = ''.join(self.buffer[:-1]).lower()

        # if self.initial_layout == 'ru':
        #     RU = str(self._RUS_CHARS+' ')
        #     US = str(self._ENG_CHARS+' ')
        #     string = ''.join(RU[US.find(s)] for s in string)

        # self.buffer = list(string) + [self.buffer[-1]]
        string = string + {'space': ' ', 'tab': '\t',
                           'enter': '\r\n'}[self.buffer[-1]]

        print(f'string =={string}==')
        self.clipboard.set_text(string, -1)
        self.delete_last_word(2 if self.buffer[-1] in ('enter') else 1)
        self.keyboard.send('ctrl+v')

    def is_upper_leadings(self):
        """"""
        string = ''.join(self.buffer)
        if (True
            and len(string) >= 2
            and string[0:2].isupper()
            and not string.isupper()
            ):
            return True
        return False

    def to_lower_leadings(self):
        """"""
        string = ''.join(self.buffer[:-1])
        string = string.lower()
        string = string + {'space': ' ', 'tab': '\t',
                           'enter': '\r\n'}[self.buffer[-1]]
        self.buffer = list(string)

    def delete_last_word(self, count: int = 1):
        for _ in range(count):
            self.keyboard.send('ctrl+backspace')

    def update_buffer(self, char: str):
        """"""
        # Если первый значимый символ после конца слова, то очищаем буфер.
        if (char in self._RUS_CHARS + self._ENG_CHARS
                and len(self.buffer) >= 2
                and self.buffer[-1] in ('space', 'tab', 'enter')):
            self.buffer.clear()

        if char in self._RUS_CHARS + self._ENG_CHARS:
            if self.keyboard.is_pressed('ctrl'):
                return
            if self.keyboard.is_pressed('shift'):
                char = self.char_upper(char)
            if self.keyboard.is_caps_locked():
                char = self.char_upper(char)
            self.buffer.append(char)
            return

        #  Символы конца строки тоже добавляем в буфер.
        if char in ('space', 'tab', 'enter'):
            self.buffer.append(char)
            return

        if char in ('backspace'):
            if self.buffer:
                self.buffer.pop()
            return

        if (char not in self._RUS_CHARS + self._ENG_CHARS
                and char not in ASWITCH_KEYS + MSWITCH_KEYS
                and char not in ('ctrl', 'shift', 'space', 'caps lock')):
            self.buffer.clear()

    def on_mouse_click(self, event):
        """"""
        print('on_mouse_click')
        self.get_layout()
        self.buffer.clear()

    def on_key_pressed(self, event):
        """"""
        key = event.key_char

        if event.type == 'down':
            self.update_buffer(key)

        if event.type == 'up':
            # if settings.SWITCH_TWOCAPS:
            #   self.caps_auto_process(key)
            if settings.SWITCH_MANUAL:
                self.kb_manual_process(key)
            if settings.SWITCH_AUTO:
                self.kb_auto_process(key)
            if key in (settings.SYS_SWITCH_KEY).split('+'):
                self.get_layout()

    def start(self):
        """"""

        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.on_key_pressed)
