import gi
gi.require_version('Gtk', '3.0')

from mouse.mouse import Mouse
from keyboard.keyboard import Keyboard
from keyboard.keymap import (EV_KEYS, VIS_KEYS)
from gi.repository import Gtk as gtk
from threading import Timer

import os
import settings
import subprocess
import time


class Switcher():
    """"""

    def __init__(self):
        """"""
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = []
        self.ngrams_ru = []
        self.ngrams_en = []

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = set(self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',)))
        self.ngrams_en = set(self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',)))

        self.username = os.environ['SUDO_USER']
        self.useruid = os.environ['SUDO_UID']
        
        self.initial_layout = self.get_layout()
        self.STILL_PRESSED = False

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
        LITERALS = 'qwertyuiopasdfghjklzxcvbnmёйцукенгшщзхъфывапролджэячсмитьбю'
        string = ''.join(filter(LITERALS.__contains__, string.lower()))

        # Для слов исключений вероятность языка неопределенная.
        # Менять раскладку автоматически для них не требуется.
        if string.strip() in settings.IGNORE_WORDS.splitlines():
            return ''

        prob_ru = sum(ng in string for ng in self.ngrams_ru)
        prob_en = sum(ng in string for ng in self.ngrams_en)

        return 'ru' if prob_ru > prob_en else 'us' if prob_ru < prob_en else ''


    def get_layout(self):
        """"""
        commands = f'sudo -u {self.username} gsettings get org.gnome.desktop.input-sources mru-sources'.split()
        return subprocess.run(commands, stdout=subprocess.PIPE).stdout.decode('utf-8')[10:12]

    def get_target_layout(self):
        """"""
        string = self.decode_buffer('us')
        string = string.replace('\t', ' ').replace('\r\n', ' ')
        layout = self.get_layout_probability(string)
        if (layout == 'ru' and self.initial_layout == 'us'): return 'ru'
        if (layout == 'us' and self.initial_layout == 'ru'): return 'us'
        return self.initial_layout

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
        commands_0 = (
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_0}"; """)

        commands_1 = (
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources mru-sources "{str_1}"; """

            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_1}\"""")

        # выполняем объединённые команды синхронно
        subprocess.run(
            ["bash", "-c", commands_0], 
            shell=False)

        # выполняем объединённые команды асинхронно
        Timer(0.2, subprocess.run, kwargs={
            'args': ["bash", "-c", commands_1],
            'shell': False}).start()

    def kb_auto_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in settings.ASWITCH_KEY_CODES
        ):
            return

        target_layout = self.get_target_layout()
        
        # не исправляем если целевая раскладка та же
        if target_layout == self.initial_layout:
            return

        # не исправляем аббревиатуры капсом
        if all(code[2:4] in ('00', '11') for code in self.buffer):
            return

        # и без этого работает, но лучше отжать для надежности
        for key in self.keyboard.active_keys():
            self.keyboard.release(key)

        self.initial_layout = target_layout
        self.set_layout(target_layout)
        
        # ждем чтобы UI наверняка успел отрисовать последний символ
        time.sleep(self.keyboard.kbdinfo().repeat.repeat / 670)

        self.delete_last_word()
        self.type_buffer()

        # взводим корректировку состояния если последняя нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.STILL_PRESSED = True

    def kb_manual_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in settings.MSWITCH_KEY_CODES
        ):
            return

        if self.initial_layout == 'ru': target_layout='us'
        if self.initial_layout == 'us': target_layout='ru'

        # и без этого работает, но лучше отжать для надежности
        for key in self.keyboard.active_keys():
            self.keyboard.release(key)

        self.initial_layout = target_layout
        self.set_layout(target_layout)
        
        # ждем чтобы UI наверняка успел отрисовать последний символ
        # time.sleep(self.keyboard.kbdinfo().repeat.repeat / 670)
        
        self.delete_last_word()
        self.type_buffer()

        # взводим корректировку состояния если последняя нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.STILL_PRESSED = True

    def caps_auto_process(self, key_code: int):
        """"""
        if (
            not self.buffer
            or key_code not in settings.MSWITCH_KEY_CODES + settings.ASWITCH_KEY_CODES
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

        # и без этого работает, но лучше отжать для надежности
        for key in self.keyboard.active_keys():
            self.keyboard.release(key)

        # ждем чтобы UI наверняка успел отрисовать последний символ
        # time.sleep(self.keyboard.kbdinfo().repeat.repeat / 670)
        
        self.delete_last_word()
        self.type_buffer()

        # взводим корректировку состояния если последняя нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.STILL_PRESSED = True

    def upper_fix_required(self):
        """"""
        string = self.decode_buffer('us')
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
            if int(key[3]) != int(key[4]):  # капс
                self.keyboard.press(42)
                self.keyboard.send([int(key[:3])])
                self.keyboard.release(42)
            else:
                self.keyboard.send([int(key[:3])])

    def encode_key(self, key_code):
        """"""
        # shift_left = 42, shift_right = 54
        encoded = list(f"{key_code:03d}00")
        encoded[3] = '1' if self.keyboard.is_pressed(42) or self.keyboard.is_pressed(54) else '0'
        encoded[4] = '1' if self.keyboard.is_caps_locked() else '0'        
        return ''.join(encoded)

    def decode_buffer(self, layout='us'):
        """"""
        string = ''
        for v in self.buffer:
            for k in EV_KEYS:
                if int(v[:3]) == k[5]:
                    if v[3] != v[4]:  # капс
                        string += k[2] if layout == 'us' else k[4]
                    else:
                        string += k[1] if layout == 'us' else k[3]
                    continue
        return string

    def update_buffer(self, key_code):
        """"""
        # Не многоязыковая клавиша или не клавиша переключения
        if (
            key_code not in VIS_KEYS
            and key_code not in settings.ASWITCH_KEY_CODES
            and key_code not in settings.MSWITCH_KEY_CODES
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
            and int(self.buffer[-1][:3]) in settings.EOW_KEY_CODES
            and (key_code in VIS_KEYS or key_code in settings.EOW_KEY_CODES)
        ):
            self.buffer.clear()

        # Многоязыковая клавиша
        if key_code in VIS_KEYS:
            self.buffer.append(self.encode_key(key_code))
            return

        # Конец слова
        if key_code in settings.EOW_KEY_CODES:
            self.buffer.append(self.encode_key(key_code))
            return

        # backspace = 14
        if key_code == 14:
            if self.buffer:
                self.buffer.pop()
            return

    def on_mouse_click(self, event):
        """"""
        self.initial_layout = self.get_layout()
        self.buffer.clear()

    def is_pressed(self, event):
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
            if self.STILL_PRESSED:
                self.STILL_PRESSED = False
                self.keyboard.send([key_code])
            # обновляем текущую раскладку при ручном переключении
            if key_char in (settings.SYS_SWITCH_KEY):
                self.initial_layout = self.get_layout()

    def start(self):
        """"""
        self.mouse.on_button_event(self.on_mouse_click)
        self.keyboard.on_key_event(self.is_pressed)


switcher = Switcher()
switcher.start()
gtk.main()