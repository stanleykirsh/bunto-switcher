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

class Switcher():
    """"""

    def __init__(self):
        """"""
        self.keyboard = Keyboard()
        self.mouse = Mouse()

        self.buffer = ['000000']

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = set(self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',)))
        self.ngrams_en = set(self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',)))

        self.username = os.environ['SUDO_USER']
        self.useruid = os.environ['SUDO_UID']
        
        self.initial_layout = self.get_layout()
        self.STILL_PRESSED = False
        self.BUFFER_LENGTH = 32

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
        LITERALS = " qwertyuiopasdfghjklzxcvbnmёйцукенгшщзхъфывапролджэячсмитьбю`,.;'[]"
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

    def get_target_layout(self, buffer):
        """"""
        # если не удалось однозначно определить целевой язык то вернет текущее значение  
        string = self.decode_buffer(buffer, layout='us', usecaps=False)
        string = string.replace('\t', ' ')
        string = string.replace('\r\n', ' ')
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
        dbus_address = f'unix:path=/run/user/{self.useruid}/bus'

        # Выполняем команды с указанием D-Bus адреса
        # Объединяем все команды в одну строку
        commands_0 = (
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_0}";""")

        commands_1 = (
            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources mru-sources "{str_1}" &"""

            f"""sudo -u {self.username} """
            f"""env DBUS_SESSION_BUS_ADDRESS={dbus_address} """
            f"""gsettings set org.gnome.desktop.input-sources sources "{str_1}" &""")

        # Запускаем и ждем завершения
        # Дождаться выполнения необходимо для корректного срабатывания следюущих команд
        subprocess.run(
            ['bash', '-c', commands_0],
            shell=False)
        
        # Запускаем и не ждем завершения
        # Запускаем с небольшой задержкой для плавности
        Timer(0.2, subprocess.run, kwargs={
            'args': ['bash', '-c', commands_1],
            'shell': False}).start()

    def kb_auto_process(self, key_code: int):
        """"""
        # get_last_word возвращает: BRAKEсловоEOW, EOWсловоEOW, BRAKEслово, EOWслово
        buffer = self.get_last_word()
        
        if (not buffer
            or key_code not in settings.ASWITCH_KEY_CODES):
            return

        # для определения языка набранного текста заменяем брейки на пробелы
        # чтобы правильно обрабатывались нграммы начала слов (" ns" = " ты")
        buf = ['05700' if int(x[:3]) in settings.EOW_KEY_CODES else x for x in buffer]
        target_layout = self.get_target_layout(buf)
        
        buffer = [x for x in buffer if int(x[:3]) not in settings.EOW_KEY_CODES]
        buffer.append(self.encode_key(key_code))
        
        # не исправляем если целевая раскладка та же
        if target_layout == self.initial_layout:
            return

        # не исправляем аббревиатуры капсом
        if all(code[2:4] in ('00', '11') for code in buffer):
            return

        self.initial_layout = target_layout
        self.set_layout(target_layout)

        # взводим корректировку состояния если последняя нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.STILL_PRESSED = True

        # sleep(0.01)

        # не печатаем брейки
        buffer = [x for x in buffer if x not in ('00000')]
        self.keyboard.type([14]*len(buffer)) # backspace = 14
        self.type_buffer(buffer)

    def kb_manual_process(self, key_code: int):
        """"""
        # get_last_word возвращает: BRAKEсловоEOW, EOWсловоEOW, BRAKEслово, EOWслово
        buffer = self.get_last_word()

        if (not buffer
            or key_code not in settings.MSWITCH_KEY_CODES):
            return

        if self.initial_layout == 'ru': target_layout='us'
        if self.initial_layout == 'us': target_layout='ru'

        self.initial_layout = target_layout
        self.set_layout(target_layout)
        
        # не печатаем брейки
        buffer = [x for x in buffer if x not in ('00000')]        
        self.keyboard.type([14]*len(buffer)) # backspace = 14
        self.type_buffer(buffer)

    def caps_auto_process(self, key_code: int):
        """"""
        # get_last_word возвращает: BRAKEсловоEOW, EOWсловоEOW, BRAKEслово, EOWслово
        buffer = self.get_last_word()        

        if (not buffer
            or key_code not in settings.MSWITCH_KEY_CODES + settings.ASWITCH_KEY_CODES):
            return

        # если в буфере первые два символа не капсом,то выходим ...
        # для этого преобразуем [BRAKEсловоEOW, EOWсловоEOW, BRAKEслово, EOWслово] => слово
        buf = [x for x in buffer if int(x[:3]) not in settings.EOW_KEY_CODES]
        if not self.upper_fix_required(buf):
            return

        # ... иначе заменяем в каждом элементе буфера, кроме первого, признаки капса на нижний регистр
        buffer = [x[:3] + '00' for x in buffer]
        buffer[1] = buffer[1][:3] + '10'
        self.buffer[-len(buffer):] = buffer

        # для определения языка набранного текста заменяем брейк на пробел
        # чтобы правильно обрабатывались нграммы начала слов (" ns" = " ты")
        buf = ['05700' if int(x[:3]) == settings.EOW_KEY_CODES else x for x in buffer]
        target_layout = self.get_target_layout(buf)

        # если требуется конвертация раскладки буфера, то выходим из процедуры
        # конвертация раскладки буфера произойдет в kb_auto_process, а капсы мы уже исправили
        if target_layout != self.initial_layout:
            return
        
        # взводим корректировку состояния если последняя нажатая клавиша еще не отжата
        if self.keyboard.is_pressed(key_code):
            self.STILL_PRESSED = True
        
        # sleep(0.01)

        # не печатаем брейки
        buffer = [x for x in buffer if x not in ('00000')]        
        self.keyboard.type([14]*len(buffer)) # backspace = 14
        self.type_buffer(buffer)

    def upper_fix_required(self, buffer):
        """"""
        string = self.decode_buffer(buffer, layout='us', usecaps=True)
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

    def get_last_word(self):
        """"""
        index = -1
        for i, k in enumerate(self.buffer[:-1]):
            if int(k[:3]) in settings.EOW_KEY_CODES:
                index = i
        return self.buffer[index:]

    def type_buffer(self, buffer):
        """"""
        for key in buffer:
            self.keyboard.release(int(key[:3]))
            # капс
            if int(key[3]) != int(key[4]):
                self.keyboard.press(42)
                self.keyboard.type([int(key[:3])])
                self.keyboard.release(42)
            # некапс
            else:
                self.keyboard.type([int(key[:3])])

    def encode_key(self, key_code):
        """"""
        # shift_left = 42, shift_right = 54
        encoded = list(f'{key_code:03d}00')
        encoded[3] = '1' if self.keyboard.is_pressed(42) or self.keyboard.is_pressed(54) else '0'
        encoded[4] = '1' if self.keyboard.is_caps_locked() else '0'        
        return ''.join(encoded)

    def decode_buffer(self, buffer, layout='us', usecaps = True):
        """"""
        string = ''
        for v in buffer:
            for k in EV_KEYS:

                if int(v[:3]) != k[5]:
                    continue

                # пробел
                if k[5] in settings.EOW_KEY_CODES:
                    string += ' '
                    break

                # капс
                if v[3] != v[4] and usecaps:
                    string += k[2] if layout == 'us' else k[4]
                # некапс
                else:
                    string += k[1] if layout == 'us' else k[3]
                break

        return string
    
    def update_buffer(self, key_code):
        """"""
        # ctrl, alt, super
        if set(self.keyboard.active_keys()) & set([29, 97, 56, 100, 125, 126]):
            self.buffer = ['00000']
            return

        # backspace = 14
        if key_code == 14:
            if self.buffer:
                self.buffer.pop()
            # если удалили всю строку в буфере, до добавляем метку начала строки
            # чтобы по нграммам правильно определился язык нового слова (" ns" = " ты")
            self.buffer = ['00000'] if not self.buffer else self.buffer
            return

        # видимый символ
        if key_code in VIS_KEYS:
            if self.keyboard.active_keys() in (29, 97): 
                return
            self.buffer.append(self.encode_key(key_code))
            if len(self.buffer) > self.BUFFER_LENGTH:
                self.buffer = self.buffer[-self.BUFFER_LENGTH:]
            return

        if (# key_code not in VIS_KEYS and
            key_code not in settings.ASWITCH_KEY_CODES and
            key_code not in settings.MSWITCH_KEY_CODES):
            self.buffer = ['00000']
            return

    def on_mouse_event(self, event):
        """"""
        self.initial_layout = self.get_layout()
        self.buffer = ['00000']

    def on_keyboard_event(self, event):
        """"""
        key_char = str(event.key_char)
        key_code = int(event.key_code)

        # KEY HOLD
        if event.type == 'hold':
            self.buffer = ['00000']
            return

        # KEY DOWN
        if event.type == 'down':
            # self.keyboard.press(key_code)
            self.update_buffer(key_code)

            if settings.SWITCH_TWOCAPS:
                self.caps_auto_process(key_code)
            if settings.SWITCH_MANUAL:
                self.kb_manual_process(key_code)
            if settings.SWITCH_AUTO:
                self.kb_auto_process(key_code)

        # KEY UP
        if event.type == 'up':
            # self.keyboard.release(key_code)
            # корректировка состояния если клавиша еще не отжата
            if self.STILL_PRESSED:
                self.STILL_PRESSED = False
                self.keyboard.type([key_code])
            # обновляем текущую раскладку при ручном переключении
            if key_char in (settings.SYS_SWITCH_KEY):
                self.initial_layout = self.get_layout()

    def start(self):
        """"""
        self.mouse.on_button_event(self.on_mouse_event)
        self.keyboard.on_key_event(self.on_keyboard_event)


switcher = Switcher()
switcher.start()
gtk.main()