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
    _EOW_KEY_CHARS = [" ", "\t", "\r\n"]
    _EOW_KEY_CODES = [57,15,28] # space, tab, enter

    _RUS_CHARS = """ё1234567890-=йцукенгшщзхъфывапролджэ\\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
    _ENG_CHARS = """`1234567890-=qwertyuiop[]asdfghjkl;'\\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""
    _SWITCHABLE_KEY_CODES = [41,2,3,4,5,6,7,8,9,10,11,12,13,43,16,17,18,19,20,21,22,23,24,25,26,27,30,31,32,33,34,35,36,37,38,39,40,44,45,46,47,48,49,50,51,52,53]

    _E = """`1234567890-=\qwertyuiop[]asdfghjkl;'zxcvbnm,./"""
    _R = """ё1234567890-=\йцукенгшщзхъфывапролджэячсмитьбю."""

    _KEY_CHARS = {41: {'ru': 'ё', 'us': '`'}, 2: {'ru': '1', 'us': '1'}, 3: {'ru': '2', 'us': '2'}, 4: {'ru': '3', 'us': '3'}, 5: {'ru': '4', 'us': '4'}, 6: {'ru': '5', 'us': '5'}, 7: {'ru': '6', 'us': '6'}, 8: {'ru': '7', 'us': '7'}, 9: {'ru': '8', 'us': '8'}, 10: {'ru': '9', 'us': '9'}, 11: {'ru': '0', 'us': '0'}, 12: {'ru': '-', 'us': '-'}, 13: {'ru': '=', 'us': '='}, 43: {'ru': '\\', 'us': '\\'}, 16: {'ru': 'й', 'us': 'q'}, 17: {'ru': 'ц', 'us': 'w'}, 18: {'ru': 'у', 'us': 'e'}, 19: {'ru': 'к', 'us': 'r'}, 20: {'ru': 'е', 'us': 't'}, 21: {'ru': 'н', 'us': 'y'}, 22: {'ru': 'г', 'us': 'u'}, 23: {'ru': 'ш', 'us': 'i'}, 24: {'ru': 'щ', 'us': 'o'}, 25: {'ru': 'з', 'us': 'p'}, 26: {'ru': 'х', 'us': '['}, 27: {'ru': 'ъ', 'us': ']'}, 30: {'ru': 'ф', 'us': 'a'}, 31: {'ru': 'ы', 'us': 's'}, 32: {'ru': 'в', 'us': 'd'}, 33: {'ru': 'а', 'us': 'f'}, 34: {'ru': 'п', 'us': 'g'}, 35: {'ru': 'р', 'us': 'h'}, 36: {'ru': 'о', 'us': 'j'}, 37: {'ru': 'л', 'us': 'k'}, 38: {'ru': 'д', 'us': 'l'}, 39: {'ru': 'ж', 'us': ';'}, 40: {'ru': 'э', 'us': "'"}, 44: {'ru': 'я', 'us': 'z'}, 45: {'ru': 'ч', 'us': 'x'}, 46: {'ru': 'с', 'us': 'c'}, 47: {'ru': 'м', 'us': 'v'}, 48: {'ru': 'и', 'us': 'b'}, 49: {'ru': 'т', 'us': 'n'}, 50: {'ru': 'ь', 'us': 'm'}, 51: {'ru': 'б', 'us': ','}, 52: {'ru': 'ю', 'us': '.'}, 53: {'ru': '.', 'us': '/'}}
    _KEY_CHARS[57] = {"ru": " ", "us": " "} # space
    _KEY_CHARS[15] = {"ru": "\t", "us": "\t"} # tab
    _KEY_CHARS[28] = {"ru": "\r\n", "us": "\r\n"} # enter

    _THREE_CHAR_KEYS = {
        "ru_shift_`": 'Ё', "us_shift_`": '~',
        "ru_shift_1": '!', "us_shift_1": '!',
        "ru_shift_2": '"', "us_shift_2": '@',
        "ru_shift_3": '№', "us_shift_3": '#',
        "ru_shift_4": ';', "us_shift_4": '$',
        "ru_shift_5": '%', "us_shift_5": '%',        
        "ru_shift_6": ':', "us_shift_6": '^',
        "ru_shift_7": '?', "us_shift_7": '&',
        "ru_shift_8": '*', "us_shift_8": '*',
        "ru_shift_9": '(', "us_shift_9": '(',
        "ru_shift_0": ')', "us_shift_0": ')',
        "ru_shift_-": '_', "us_shift_-": '_',
        "ru_shift_=": '+', "us_shift_=": '+',        
        "ru_shift_'": 'Э', "us_shift_'": '"',
        "ru_shift_/": ',', "us_shift_/": '?',
        "ru_shift_\\": '/', "us_shift_\\": '|',
        }

    _ALL_CHARS = _RUS_CHARS + _ENG_CHARS

    _RUS_ENG = dict(zip(_RUS_CHARS, _ENG_CHARS))
    _ENG_RUS = dict(zip(_ENG_CHARS, _RUS_CHARS))

    _ASWITCH_KEYS = ['space', 'tab']
    _MSWITCH_KEYS = ['pause']

    _ASWITCH_KEY_CODES = [57, 15] # space, tab
    _MSWITCH_KEY_CODES = [119] # pause

    def __init__(self):
        """"""
        self.clipboard = Clipboard()
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.__buffer__ = []
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
                source = "ru"
            case 'ru':
                source = "us"

        return ''.join(
            self._KEY_CHARS[int(key_code[:3])][source]
                for key_code in self.__buffer__)
        
        # Игнорировать space, enter, tab...
        """_EXCEPTIONS = ("space", "tab", "enter")
        match self.initial_layout:
            case 'us':
                return ''.join(self._ENG_RUS[s] if (s in self._ENG_RUS and s not in _EXCEPTIONS) else s for s in string)
            case 'ru':
                return ''.join(self._RUS_ENG[s] if (s in self._RUS_ENG and s not in _EXCEPTIONS) else s for s in string)
        return string"""

    def translit2en(self, string: str):
        if self.initial_layout == 'ru':
            return ''.join(self._ENG_RUS[s] if s in self._ENG_RUS else s for s in string)
        return string

    def kb_auto_process(self, char: str):
        """"""
        if (
            char not in self._ASWITCH_KEYS
            or not self.buffer
        ):
            return

        target_layout = self.get_target_layout()
        if not target_layout:
            return
        
        # string = ''.join(self.buffer[:-1])
        string = self.decode___buffer_(target_layout=target_layout)
        # string = self.switch_language(string)

        """if self.buffer[-1] in self._EOW_KEYS:
            string = string + self._EOW_KEYS[self.buffer[-1]]"""

        self.keyboard.release(char)
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        self.keyboard.send(SYS_SWITCH_KEY)
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
        
        if self.initial_layout == "ru": target_layout="us"
        if self.initial_layout == "us": target_layout="ru"
        string = self.decode___buffer_(target_layout=target_layout)
        # string = self.switch_language(string)

        """if self.buffer[-1] in self._EOW_KEYS:
            string = ''.join(self.buffer[:-1])
            string = self.switch_language(string)
            string = string + self._EOW_KEYS[self.buffer[-1]]
        else:
            string = ''.join(self.buffer)
            string = self.switch_language(string)"""

        self.keyboard.release(char)        
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        self.keyboard.send(SYS_SWITCH_KEY)
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

        """self.buffer = [self.buffer[0]] + \
            list(''.join(self.buffer[1:-1]).lower()) + [self.buffer[-1]]"""
        
        # buffer = []
        for index, encoded_key in enumerate(self.__buffer__):
            encoded_key = list(encoded_key)
            encoded_key[3] = "0" if index != 0 else "1"
            encoded_key[4] = "0"
            self.__buffer__[index] = "".join(encoded_key)

        target_layout = self.get_target_layout()
        if target_layout:
            return
        
        string = self.decode___buffer_(target_layout)

        """if self.buffer[-1] in self._EOW_KEYS:
            string = ''.join(self.buffer[:-1])
            string = string[0] + string[1:].lower()
            string = self.translit2en(string)
            string = string + self._EOW_KEYS[self.buffer[-1]]
        else:
            string = ''.join(self.buffer)
            string = string[0] + string[1:].lower()
            string = self.translit2en(string)"""

        self.keyboard.release(char)        
        self.clipboard.save()
        self.clipboard.set_text(string)
        self.delete_last_word()
        self.keyboard.send('ctrl_left+v')
        Timer(0.20, self.clipboard.restore).start()

    def get_target_layout(self):
        """"""
        # string = ''.join(self.buffer)
        string = self.decode___buffer_()
        # string = string.replace('shift_left+', '')
        # string = string.replace('shift_right+', '')
        # string = string.replace('space', ' ')
        # string = string.replace('tab', ' ')
        probability = self.layout_probability(string)
        if (probability == 'ru' and self.initial_layout == 'us'): return "ru"
        if (probability == 'us' and self.initial_layout == 'ru'): return "us"
        # return True
        return False

    def upper_fix_required(self):
        """"""
        # string = ''.join(self.buffer[:-1])
        string = self.decode___buffer_()
        if (
            len(string) >= 2
            and string[0:2].isupper()
            and not string.isupper()
        ):
            return True
        return False

    def delete_last_word(self):
        """"""
        self.keyboard.type(["backspace"]*len(self.buffer))

    def encode_key(self, key_code):
        """"""

        # Convert the key code to a n-digit string
        encoded = ("00" + str(key_code))[-3:] + "0000"

        # Convert the encoded string to a list for easier manipulation
        encoded_list = list(encoded)

        if self.keyboard.is_pressed('shift_left') or self.keyboard.is_pressed('shift_right'):
            encoded_list[3] = "1"

        if self.keyboard.is_caps_locked():            
            encoded_list[4] = "1"

        """if self.keyboard.is_pressed("ctrl_left") or self.keyboard.is_pressed("ctrl_right"):
            encoded_list[5] = "1"

        if self.keyboard.is_pressed("alt_left") or self.keyboard.is_pressed("alt_right"):            
            encoded_list[6] = "1"

        if self.keyboard.is_pressed("win_left") or self.keyboard.is_pressed("win_right"):            
            encoded_list[7] = "1"""

        return "".join(encoded_list)

    def decode___buffer_(self, target_layout="us"):
        """"""
        decoded_str = ""
        for key in self.__buffer__:

            key_code = int(key[:3])
            capitalize = abs(int(key[3])-int(key[4]))

            # Печатный символ
            if key_code in self._KEY_CHARS:
                char = self._KEY_CHARS[key_code][target_layout]
                if capitalize:
                    char = char.upper()

            decoded_str += char
            print(decoded_str)
        return decoded_str

    def update___buffer__(self, event):
        """"""
        key_char = str(event.key_char)
        key_code = int(event.key_code)

        # Не многоязыковая клавиша или не клавиша переключения
        if (
                key_code not in self._ASWITCH_KEY_CODES
                and key_char in self._MSWITCH_KEY_CODES
                and key_code not in (29, 97, 42, 54, 57, 58)
                # ctrl_left, ctrl_right, shift_left, shift_right, space, caps_lock
            ):
            self.__buffer__.clear()
            return

        # Ctrl + любая клавиша чистят буфер и не добавляет эту букву в буфер.
        if self.keyboard.is_pressed("ctrl_left") or self.keyboard.is_pressed("ctrl_right"):
            self.__buffer__.clear()
            return

        # Если приходит первый значимый символ после конца слова, то очищаем буфер.
        # Первое условие обязательно первое чтобы при пустом буфере не падало второе.
        if (
            self.__buffer__
            and int(self.__buffer__[-1][:3]) in self._EOW_KEY_CODES
            and (key_code in self._SWITCHABLE_KEY_CODES or key_code in self._EOW_KEY_CODES)
        ):
            self.__buffer__.clear()

        # Многоязыковая клавиша
        if key_code in self._SWITCHABLE_KEY_CODES:
            self.__buffer__.append(self.encode_key(key_code))
            return

        # End of word key
        if key_code in self._EOW_KEY_CODES:
            self.__buffer__.append(self.encode_key(key_code))
            return

        # Backspace
        if key_code == 14:
            if self.__buffer__:
                self.__buffer__.pop()
            return       
        

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

            # Ctrl + любая буква (например, ctrl + v) чистят буфер и не добавляет эту букву в буфер.
            if self.keyboard.is_pressed('ctrl_left') or self.keyboard.is_pressed('ctrl_right'):
                self.buffer.clear()
                return

            """if (char in '0123456789'
                and not self.keyboard.is_pressed('shift_left') 
                and not self.keyboard.is_pressed('shift_right')):
                self.buffer.clear()
                return"""            

            # Shift ...
            if self.keyboard.is_pressed('shift_left') or self.keyboard.is_pressed('shift_right'):
                code = f'{self.initial_layout}_shift_{char}'
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

        if char not in self._ALL_CHARS:

            #  Символы конца строки тоже добавляем в буфер.
            if char in self._EOW_KEYS:  # ('space', 'tab', 'enter'):
                self.buffer.append(char)
                return

            if char in ('backspace'):
                if self.buffer:
                    self.buffer.pop()
                return

            if (
                    char not in self._ASWITCH_KEYS + self._MSWITCH_KEYS
                    and char not in ('ctrl_left', 'ctrl_right', 'shift_left', 'shift_right', 'space', 'caps_lock')
                ):
                self.buffer.clear()

    def on_mouse_click(self, event):
        """"""
        self.get_layout()
        self.buffer.clear()

    def on_key_pressed(self, event):
        """"""
        if event.type == 'down':
            self.update_buffer(event.key_char)
            self.update___buffer__(event)
            # print(self.__buffer__)
            """d = {}
            for i, v in enumerate(self._SWITCHABLE_KEY_CODES):
                kk = self._SWITCHABLE_KEY_CODES[i]
                cyr = self._R[i]
                lat = self._E[i]
                d[kk] = {"ru":cyr, "us":lat}
            print(d)"""

            if settings.SWITCH_TWOCAPS:                
                self.caps_auto_process(event.key_char)
            if settings.SWITCH_MANUAL:
                self.kb_manual_process(event.key_char)
            if settings.SWITCH_AUTO:
                self.kb_auto_process(event.key_char)
            if event.key_char in (settings.SYS_SWITCH_KEY).split('+'):
                self.get_layout()            

    def start(self):
        """"""
        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.on_key_pressed)


switcher = Switcher()
switcher.start()
gtk.main()
