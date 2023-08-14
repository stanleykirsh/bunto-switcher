from mouse.mouse import Mouse
from keyboard.keyboard import Keyboard
from settings import SYS_SWITCH_KEY
from gi.repository import Gtk, Gdk
from threading import Timer

import os
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

    _ASWITCH_KEYS = ['space', 'tab']
    _MSWITCH_KEYS = ['pause']


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

        if string in settings.IGNORE_WORDS.split('|'):
            return ''

        print(string)

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

    def kb_switch_layout(self):
        """"""
        self.keyboard.send(SYS_SWITCH_KEY)

    def kb_auto_process(self, char: str):
        """"""
        if char not in self._ASWITCH_KEYS:
            return

        if not self.lang_fix_required():
            return

        self.delete_last_word()

        string = ''.join(self.buffer[:-1])
        string = self.translit(string)
        string_ends = {'space': ' ', 'tab': '\t', 'enter': '\r\n'}
        if self.buffer[-1] in string_ends:
            string = string + string_ends[self.buffer[-1]]    

        self.clipboard.set_text(string, -1)
        self.keyboard.grab()
        self.keyboard.send('ctrl+v')
        self.kb_switch_layout()
        self.keyboard.ungrab()
        Timer(0.1, self.get_layout).start()

    def kb_manual_process(self, char: str):
        """"""
        if char not in self._MSWITCH_KEYS:
            return

        self.delete_last_word()
        
        string = ''.join(self.buffer[:-1])
        string = self.translit(string)
        string_ends = {'space': ' ', 'tab': '\t', 'enter': '\r\n'}
        if self.buffer[-1] in string_ends:
            string = string + string_ends[self.buffer[-1]]      

        self.clipboard.set_text(string, -1)
        self.keyboard.grab()
        self.keyboard.send('ctrl+v')
        self.kb_switch_layout()
        self.keyboard.ungrab()
        Timer(0.1, self.get_layout).start()

    def caps_auto_process(self, char: str):
        """"""
        if char not in self._MSWITCH_KEYS + self._ASWITCH_KEYS:
            return

        # если в буфере первые два символа не капсом,то выходим
        if not self.upper_fix_required():
            return

        self.buffer = [self.buffer[0]] + list(''.join(self.buffer[1:-1]).lower()) + [self.buffer[-1]]

        if self.lang_fix_required():
            return

        self.delete_last_word()

        string = ''.join(self.buffer[:-1])
        string = string[0] + string[1:].lower()
        
        if self.initial_layout == 'ru':
            RU = str(self._RUS_CHARS+' ')
            US = str(self._ENG_CHARS+' ')
            string = ''.join(RU[US.find(s)] for s in string)        
        
        string_ends = {'space': ' ', 'tab': '\t', 'enter': '\r\n'}
        if self.buffer[-1] in string_ends:
            string = string + string_ends[self.buffer[-1]] 

        self.clipboard.set_text(string, -1)
        self.keyboard.grab()
        self.keyboard.send('ctrl+v')
        self.keyboard.unrab()

    def lang_fix_required(self):
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

    def upper_fix_required(self):
        """"""
        string = ''.join(self.buffer)
        if (True
            and len(string) >= 2
            and string[0:2].isupper()
            and not string.isupper()
            ):
            return True
        return False

    def delete_last_word(self):
        """"""
        special_chars = [
            "`", "[", "]", ";", "'", ",", ".", "/",
            "~", "{", "}", ":", '"', "<", ">", "?",
            ]        
        # проверяем что хотя бы одно значение из bad_chars имеется в буфере
        # OC нестабильно удаляет по ctrl+space последнее слово которое содержат эти символы
        # поэтому такие слова удаляем медленным но надежным backspace
        if any(map(lambda v: v in self.buffer, special_chars)):
            for _ in self.buffer:
                self.keyboard.send('backspace')
        # если буфер не содержит особых символов, то удалем быстрым способом
        else:
            self.keyboard.send('ctrl+backspace')

    def update_buffer(self, char: str):
        """"""
        # Если первый значимый символ после конца слова, то очищаем буфер.
        if (char in self._RUS_CHARS + self._ENG_CHARS
                and len(self.buffer) >= 2
                and self.buffer[-1] in ('space', 'tab', 'enter')):
            print('buffer.clear 1')
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
                and char not in self._ASWITCH_KEYS + self._MSWITCH_KEYS
                and char not in ('ctrl', 'shift', 'space', 'caps lock')):
            print('buffer.clear 2')
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
