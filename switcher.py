import gi
gi.require_version('Gtk', '3.0')

from mouse.mouse import Mouse
from keyboard.keyboard import Keyboard
# from clipboard.clipboard import Clipboard
from gi.repository import Gtk as gtk
# from settings import SYS_SWITCH_KEY
# from threading import Timer
from charmap import (
    EOW_KEY_CODES,
    ASWITCH_KEY_CODES,
    MSWITCH_KEY_CODES,
    # INSERT_KEY_CODE,
    KEY_MAP)

import os
import settings
import subprocess


class Switcher():
    """"""

    def __init__(self):
        """"""
        # self.clipboard = Clipboard()
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.ngrams_ru = []
        self.ngrams_en = []

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = set(self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',)))
        self.ngrams_en = set(self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',)))

        self.username = os.environ['SUDO_USER']
        self.useruid = self.get_user_uid(self.username)
        self.initial_layout = self.get_layout()
        # print("initial_layout", self.initial_layout)

        self.PRESSED = False

    def load_ngrams(self, filenames):
        """"""
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def get_layout_probability(self, string: str):
        """"""
        LITERALS = '''qwertyuiopasdfghjklzxcvbnmёйцукенгшщзхъфывапролджэячсмитьбю'''

        string = string.lower()
        string = ''.join([s for s in string if s in LITERALS])

        # Для слов исключений вероятность языка неопределенная.
        # Менять раскладку автоматически для них не требуется.
        if string.strip() in settings.IGNORE_WORDS.splitlines():
            return ''

        prob_ru = sum((1 for ng in self.ngrams_ru if ng in string))
        prob_en = sum((1 for ng in self.ngrams_en if ng in string))

        if prob_ru > prob_en: return 'ru'
        if prob_ru < prob_en: return 'us'
        if prob_ru == prob_en: return ''

    def get_layout(self):
        """"""
        get_mru_sources = f'sudo -u {self.username} gsettings get org.gnome.desktop.input-sources mru-sources'.split()
        result = subprocess.run(get_mru_sources, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8')[10:12]
        self.initial_layout = result
        return result

    def get_target_layout(self):
        """"""
        # print('get_target_layout', self.buffer, self.initial_layout)
        string = self.decode_buffer()
        string = string.replace('\t', ' ')
        string = string.replace('\r\n', ' ')
        return self.get_layout_probability(string)

    def get_user_uid(self, user):
        """"""
        # Получаем информацию о пользователе
        result = subprocess.run(
            ['id', '-u', user],
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()


    def set_layout(self, layout: str):
        """"""        
        if layout == 'ru':
            str_0 = "[('xkb','ru')]"
            str_1 = "[('xkb','ru'),('xkb','us')]"

        if layout == 'us':
            str_0 = "[('xkb','us')]"
            str_1 = "[('xkb','us'),('xkb','ru')]"

        # Формируем путь к D-Bus сессии        
        dbus_address = f"unix:path=/run/user/{self.useruid}/bus"

        # Выполняем команды с указанием D-Bus адреса
        # Объединяем все команды в одну строку
        commands = (
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_0}"; """
            
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources mru-sources "{str_1}"; """
            
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_1}\"""")

        # Выполняем объединённые команды
        subprocess.run(
            ["bash", "-c", commands],
            # check=True,
            shell=False
        )

    def kb_auto_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in ASWITCH_KEY_CODES
        ):
            return

        target_layout = self.get_target_layout()
        
        # не исправляем если раскладка та же
        if target_layout == self.initial_layout:
            return

        # не исправляем аббревиатуры капсом
        if all(code[2:4] in ('00', '11') for code in self.buffer):
            return
        
        self.initial_layout = target_layout        
        self.set_layout(target_layout)
        self.delete_last_word()
        self.type_buffer()

        # корректировка состояния если нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.PRESSED = True

    def kb_manual_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in MSWITCH_KEY_CODES
        ):
            return

        if self.initial_layout == 'ru': target_layout='us'
        if self.initial_layout == 'us': target_layout='ru'

        self.initial_layout = target_layout
        self.set_layout(target_layout)
        self.delete_last_word()
        self.type_buffer()

    def caps_auto_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in MSWITCH_KEY_CODES + ASWITCH_KEY_CODES            
        ):
            return

        # если в буфере первые два символа не капсом,то выходим
        if not self.upper_fix_required():
            return
        
        # заменяем в каждом элементе буфера (кроме первого) признаки капса на нижний регистр
        for i in range(1, len(self.buffer)):
            self.buffer[i] = self.buffer[i][:3] + '00'

        # если требуется конвертация раскладки буфера, то выходим из процедуры
        # конвертация раскладки буфера произойдет в kb_auto_process, а раскладку буфера мы уже поменяли
        if self.get_target_layout() != self.initial_layout:
            return

        self.delete_last_word()
        self.type_buffer()

    def upper_fix_required(self):
        """"""
        string = self.decode_buffer()
        # ИСправление
        if (len(string) >= 2
            and string[0:2].isupper()
            and not string.isupper()):
            return True        
        # исПРАВЛЕНИЕ
        if (len(string) >= 2
            and string[0:2].islower()
            and not string.islower()):
            return True
        return False

    def delete_last_word(self):
        """"""
        # backspace = 14
        self.keyboard.send([14]*len(self.buffer))

    def type_buffer(self):
        """"""
        for key in self.buffer:
            if int(key[3]):
                self.keyboard.press(42)
                self.keyboard.send([int(key[:3])])
                self.keyboard.release(42)
            else:
                self.keyboard.send([int(key[:3])])

    def encode_key(self, key_code):
        """"""
        encoded = ('00' + str(key_code))[-3:] + '00'
        encoded_list = list(encoded)

        # shift_left = 42, shift_right = 54
        if self.keyboard.is_pressed(42) or self.keyboard.is_pressed(54):
            encoded_list[3] = '1'

        if self.keyboard.is_caps_locked():
            encoded_list[4] = '1'

        return "".join(encoded_list)

    def decode_buffer(self, target_layout='us'):
        """"""
        decoded_str = ""
        for key in self.buffer:

            key_code = int(key[:3])
            is_capitalized = bool(int(key[3]) != int(key[4]))

            _target_layout = target_layout + '_' if is_capitalized else target_layout

            if key_code in KEY_MAP:
                char = KEY_MAP[key_code][_target_layout]

            decoded_str += char
        return decoded_str

    def update_buffer(self, key_code):
        """"""
        # Не многоязыковая клавиша или не клавиша переключения
        if (
                key_code not in KEY_MAP
                and key_code not in ASWITCH_KEY_CODES
                and key_code not in MSWITCH_KEY_CODES
                and key_code not in (29, 97, 42, 54, 57, 58)
                # ctrl_left, ctrl_right, shift_left, shift_right, space, caps_lock
            ):
            self.buffer.clear()
            return

        # Ctrl + любая клавиша чистят буфер и не добавляет эту букву в буфер.
        # ctrl_left = 29, ctrl_right = 97
        if self.keyboard.is_pressed(29) or self.keyboard.is_pressed(97):
            self.buffer.clear()
            return

        # Если приходит первый значимый символ после конца слова, то очищаем буфер.
        # Первое условие обязательно первое чтобы при пустом буфере не падало второе.
        if (
            self.buffer
            and int(self.buffer[-1][:3]) in EOW_KEY_CODES
            and (key_code in KEY_MAP or key_code in EOW_KEY_CODES)
        ):
            self.buffer.clear()

        # Многоязыковая клавиша
        if key_code in KEY_MAP:
            self.buffer.append(self.encode_key(key_code))
            return

        # Конец слова
        if key_code in EOW_KEY_CODES:
            self.buffer.append(self.encode_key(key_code))
            return

        # backspace = 14
        if key_code == 14:
            if self.buffer:
                self.buffer.pop()
            return

    def on_mouse_click(self, event):
        """"""
        self.get_layout()
        self.buffer.clear()

    def on_key_pressed(self, event):
        """"""
        key_char = str(event.key_char)
        key_code = int(event.key_code)
        
        if event.type == 'down':           
            self.update_buffer(key_code)

            if settings.SWITCH_TWOCAPS:                
                self.caps_auto_process(key_code)
            if settings.SWITCH_MANUAL:
                self.kb_manual_process(key_code)
            if settings.SWITCH_AUTO:
                self.kb_auto_process(key_code)

        if event.type == 'up':
            # корректировка состояния если нажатая клавиша еще не отжата
            if self.PRESSED:
                self.PRESSED = False
                self.keyboard.send([key_code])        
            # обновляем текущую раскладку при ручном переключении
            if key_char in (settings.SYS_SWITCH_KEY):
                self.get_layout()

    def start(self):
        """"""
        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.on_key_pressed)


switcher = Switcher()
switcher.start()
gtk.main()