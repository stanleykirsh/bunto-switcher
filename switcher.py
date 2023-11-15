import gi
gi.require_version('Gtk', '3.0')

from mouse.mouse import Mouse
from keyboard.keyboard import Keyboard
from clipboard.clipboard import Clipboard
from gi.repository import Gtk as gtk
from settings import SYS_SWITCH_KEY
from threading import Timer
from time import sleep

import os
import settings
import subprocess
          

class Switcher():
    """"""
    _EOW_KEYS = {'space': ' ', 'tab': '\t', 'enter': '\r\n'}

    _RUS_CHARS = """ё1234567890-=йцукенгшщзхъфывапролджэ\\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
    _ENG_CHARS = """`1234567890-=qwertyuiop[]asdfghjkl;'\\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

    _THREE_CHAR_KEYS = {
        "ru_shift_`": 'Ё',
        "us_shift_`": '~',
        "ru_shift_2": '"',
        "us_shift_2": '@',
        "ru_shift_3": '№',
        "us_shift_3": '#',
        "ru_shift_4": ';',
        "us_shift_4": '$',
        "ru_shift_6": ':',
        "us_shift_6": '^',
        "ru_shift_7": '?',
        "us_shift_7": '&',
        "ru_shift_'": 'Э',
        "us_shift_'": '"',
        "ru_shift_/": ',',
        "us_shift_/": '?',
        }

    _ALL_CHARS = _RUS_CHARS + _ENG_CHARS

    _RUS_ENG = dict(zip(_RUS_CHARS, _ENG_CHARS))
    _ENG_RUS = dict(zip(_ENG_CHARS, _RUS_CHARS))

    _ASWITCH_KEYS = ['space', 'tab']
    _MSWITCH_KEYS = ['pause']

    def __init__(self):
        """"""
        self.clipboard = Clipboard()
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.ngrams_ru = []
        self.ngrams_en = []

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = set(self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',)))
        self.ngrams_en = set(self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',)))

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

        # Для слов исключений вероятность языка неопределенная.
        # Менять раскладку автоматически для них не требуется.
        if (
            self.translit2en(string.strip())
            and string.strip() in settings.IGNORE_WORDS.splitlines()
        ):
            return ''

        prob_ru = 0
        for ngram in self.ngrams_ru:
            if ngram in string:
                prob_ru += 1

        prob_en = 0
        for ngram in self.ngrams_en:
            if ngram in string:
                prob_en += 1

        if prob_ru > prob_en:
            return 'ru'
        if prob_ru < prob_en:
            return 'us'
        if prob_ru == prob_en:
            return ''

    def get_layout(self):
        """"""
        # рабочий вариант для X11:
        # print('get_layout', self.xkb.group_symbol)
        # return self.xkb.group_symbol
        get_mru_sources = f'sudo -u {self.username} gsettings get org.gnome.desktop.input-sources mru-sources'.split()
        result = subprocess.run(get_mru_sources, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8')[10:12]
        self.initial_layout = result
        return result

    def switch_language(self, string: str):
        """"""
        match self.initial_layout:
            case 'us':
                return ''.join(self._ENG_RUS[s] if s in self._ENG_RUS else s for s in string)
            case 'ru':
                return ''.join(self._RUS_ENG[s] if s in self._RUS_ENG else s for s in string)
        return string

    def translit2en(self, string: str):
        if self.initial_layout == 'ru':
            return ''.join(self._ENG_RUS[s] if s in self._ENG_RUS else s for s in string)
        return string

    def kb_switch_layout(self):
        """"""
        self.keyboard.send(SYS_SWITCH_KEY)

    def kb_auto_process(self, char: str):
        """"""
        if (
            char not in self._ASWITCH_KEYS
            or not self.buffer
        ):
            return

        if not self.lang_fix_required():
            return
        
        string = ''.join(self.buffer[:-1])
        string = self.switch_language(string)

        if self.buffer[-1] in self._EOW_KEYS:
            string = string + self._EOW_KEYS[self.buffer[-1]]

        self.keyboard.release(char)
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        self.kb_switch_layout()
        Timer(0.20, self.clipboard.restore).start()
        Timer(0.30, self.get_layout).start()

    def kb_manual_process(self, char: str):
        """"""
        if (
            char not in self._MSWITCH_KEYS
            or not self.buffer
            or (
                len(self.buffer) == 1 and
                self.buffer[-1] in self._EOW_KEYS
                )
        ):
            return

        if self.buffer[-1] in self._EOW_KEYS:
            string = ''.join(self.buffer[:-1])
            string = self.switch_language(string)
            string = string + self._EOW_KEYS[self.buffer[-1]]
        else:
            string = ''.join(self.buffer)
            string = self.switch_language(string)

        self.keyboard.release(char)        
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        self.kb_switch_layout()
        Timer(0.20, self.clipboard.restore).start()
        Timer(0.30, self.get_layout).start()

    def caps_auto_process(self, char: str):
        """"""
        if (
            char not in self._MSWITCH_KEYS + self._ASWITCH_KEYS
            or not self.buffer
        ):
            return

        # если в буфере первые два символа не капсом,то выходим
        if not self.upper_fix_required():
            return

        self.buffer = [self.buffer[0]] + \
            list(''.join(self.buffer[1:-1]).lower()) + [self.buffer[-1]]

        if self.lang_fix_required():
            return

        if self.buffer[-1] in self._EOW_KEYS:
            string = ''.join(self.buffer[:-1])
            string = string[0] + string[1:].lower()
            string = self.translit2en(string)
            string = string + self._EOW_KEYS[self.buffer[-1]]
        else:
            string = ''.join(self.buffer)
            string = string[0] + string[1:].lower()
            string = self.translit2en(string)

        self.keyboard.release(char)        
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        Timer(0.20, self.clipboard.restore).start()

    def lang_fix_required(self):
        """"""
        string = ''.join(self.buffer)
        string = string.replace('shift_left+', '')
        string = string.replace('shift_right+', '')
        string = string.replace('space', ' ')
        string = string.replace('tab', ' ')
        probability = self.layout_probability(string)
        if ((probability == 'ru' and self.initial_layout == 'us')
                or (probability == 'us' and self.initial_layout == 'ru')):
            return True
        return False

    def upper_fix_required(self):
        """"""
        string = ''.join(self.buffer[:-1])
        if (
            len(string) >= 2
            and string[0:2].isupper()
            and not string.isupper()
        ):
            return True
        return False

    def delete_last_word(self):
        """"""
        for _ in self.buffer:
            self.keyboard.send('backspace')

    def update_buffer(self, char: str):
        """"""
        # Если приходит первый значимый символ после конца слова, то очищаем буфер.
        # Первое условие обязательно первое чтобы при пустом буфере не падало второе.
        if (
            self.buffer
            and self.buffer[-1] in self._EOW_KEYS
            and (
                char in self._ALL_CHARS
                or char in self._EOW_KEYS
            )
        ):
            self.buffer.clear()

        if char in self._ALL_CHARS:

            # Ctrl + любая буква (напрмер, ctrl + v) чистят буфер и не добавляет эту букву в буфер.
            if self.keyboard.is_pressed('ctrl_left') or self.keyboard.is_pressed('ctrl_right'):
                self.buffer.clear()
                return

            # Shift ...
            if self.keyboard.is_pressed('shift_left') or self.keyboard.is_pressed('shift_right'):
                code = f'{self.initial_layout}_shift_{char}'
                print(code)
                if code in self._THREE_CHAR_KEYS:
                    char = self._THREE_CHAR_KEYS[code]
                
            # Shift + любая буква переводят нажатую букву в верхний регистр.
            if self.keyboard.is_pressed('shift_left') or self.keyboard.is_pressed('shift_right'):
                char = char.upper()

            # Включенный капс переводит нажатую букву в верхний регистр.
            if self.keyboard.is_caps_locked():
                char = char.upper()
            
            self.buffer.append(char)
            return

        #  Символы конца строки тоже добавляем в буфер.
        if char in self._EOW_KEYS:  # ('space', 'tab', 'enter'):
            self.buffer.append(char)
            return

        if char in ('backspace'):
            if self.buffer:
                self.buffer.pop()
            return

        if (char not in self._ALL_CHARS
                and char not in self._ASWITCH_KEYS + self._MSWITCH_KEYS
                and char not in ('ctrl_left', 'ctrl_right', 'shift_left', 'shift_right', 'space', 'caps_lock')
            ):
            self.buffer.clear()

    def on_mouse_click(self, event):
        """"""
        print('on_mouse_click')
        self.get_layout()
        self.buffer.clear()

    def on_key_pressed(self, event):
        """"""
        key = event.key_char

        if event.type == 'hold':
            self.buffer.clear()
            sleep(0.5)
            return

        if event.type == 'down':
            self.update_buffer(key)

            if settings.SWITCH_TWOCAPS:                
                self.caps_auto_process(key)
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


switcher = Switcher()
switcher.start()
gtk.main()
