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

        self.buffer = ['00000']

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.ngrams_ru = self.load_ngrams((f'{dir_path}/data/ngrams-ru.txt',))
        self.ngrams_en = self.load_ngrams((f'{dir_path}/data/ngrams-en.txt',))

        self.username = os.environ['SUDO_USER']
        self.useruid = os.environ['SUDO_UID']
        
        self.initial_layout = self.get_layout()

    def load_ngrams(self, filenames):
        """"""
        result = []
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
                result.extend(lines)
        return result

    def split_into_ngrams(self, string, min_len=2, max_len=4):
        """
        Разбивает строку на n-граммы заданной длины, выделяя:
        - n-граммы, начинающиеся с пробела (левая сторона)
        - n-граммы из центральной части (без крайних пробелов)
        - n-граммы, заканчивающиеся пробелом (правая сторона)
        
        Параметры:
        string (str): входная строка
        min_len (int): минимальная длина n-граммы
        max_len (int): максимальная длина n-граммы
        
        Возвращает:
        list: объединённый список n-грамм (левые + центральные + правые)
        """

        def _split_into_ngrams_(s, min_len, max_len):
            """Вспомогательная функция для генерации n-грамм из строки."""
            result = []
            n = len(s)

            for i in range(n):
                for length in range(min_len, max_len + 1):
                    if i + length <= n:
                        substring = s[i:i + length]
                        if ' ' not in substring.strip():
                            result.append(substring)
            return result
        
        # Генерируем n-граммы для всей строки (с пробелами по краям)
        result_sides = _split_into_ngrams_(string, min_len, max_len)

        # Генерируем n-граммы для центральной части (без крайних пробелов)
        stripped = string.strip()
        if len(stripped) > 2:
            center_part = stripped[1:-1]
            result_center = _split_into_ngrams_(center_part, min_len, max_len)
        else:
            result_center = []

        # Фильтруем n-граммы по позициям пробелов
        result_left = [x for x in result_sides if x[0] == ' ']
        result_right = [x for x in result_sides if x[-1] == ' ']

        # Объединяем результаты
        result = list(set(result_left + result_center + result_right))
        return result

    def get_layout_probability(self, string: str):
        """"""
        LITERALS = " qwertyuiopasdfghjklzxcvbnmёйцукенгшщзхъфывапролджэячсмитьбю`,.;'[]"
        string = ''.join(filter(LITERALS.__contains__, string.lower()))

        # Для слов исключений вероятность языка неопределенная.
        # Менять раскладку автоматически для них не требуется.
        """if string.strip() in settings.IGNORE_WORDS.splitlines():
            return ''"""

        ngrams = self.split_into_ngrams(string=string, min_len=2, max_len=4)

        prob_ru = sum(ng in self.ngrams_ru for ng in ngrams)
        prob_en = sum(ng in self.ngrams_en for ng in ngrams)

        # prob_ru = sum(ng in string for ng in self.ngrams_ru)
        # prob_en = sum(ng in string for ng in self.ngrams_en)

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
        Timer(0.0, subprocess.run, kwargs={
            'args': ['bash', '-c', commands_1],
            'shell': False}).start()

    def kb_auto_process(self, key_code: int):
        """"""
        buffer = self.buffer
        
        if (not buffer or
            key_code == 14 or  # backspace
            key_code not in VIS_KEYS):
            return
        
        # удаляем все пробелы и брейки слева и справа 
        # т.к. кто знает сколько их там. осталяем чистый текст
        buffer = [x for x in buffer if x[:4] not in settings.EOW_KEY_CODES]

        # добавляем в начало и конец по пробелу чтобы правильно 
        # обрабатывались нграммы начала слов (" ns " = " ты ")
        # target_layout = self.get_target_layout(['05700'] + buffer + ['05700'])
        target_layout = self.get_target_layout(['05700'] + buffer)

        # не исправляем если целевая раскладка та же
        if target_layout == self.initial_layout:
            return

        # не исправляем аббревиатуры капсом
        if all(code[2:4] in ('00', '11') for code in buffer):
            return

        # возвращаем в конец буфера последнюю нажатую клавишу
        # buffer.append(self.encode_key(key_code))
        
        self.initial_layout = target_layout
        self.set_layout(target_layout)

        self.keyboard.type([14]*len(buffer)) # backspace = 14
        self.type_buffer(buffer)

    def kb_manual_process(self, key_code: int):
        """"""
        buffer = self.buffer[1:]

        if (not buffer or
            key_code not in settings.MSWITCH_KEY_CODES):
            return

        if self.initial_layout == 'ru': target_layout='us'
        if self.initial_layout == 'us': target_layout='ru'

        # возвращаем в конец буфера последнюю нажатую клавишу
        # buffer.append(self.encode_key(key_code))

        self.initial_layout = target_layout
        self.set_layout(target_layout)
        
        # не печатаем брейки
        # buffer = [x for x in buffer if x not in ('00000')]        
        
        self.keyboard.type([14]*len(buffer)) # backspace = 14
        self.type_buffer(buffer)

    def caps_auto_process(self, key_code: int):
        """"""
        buffer = self.buffer

        if (not buffer or
            key_code not in settings.MSWITCH_KEY_CODES + settings.ASWITCH_KEY_CODES):
            return

        # удаляем все пробелы и брейки слева и справа 
        # т.к. кто знает сколько их там. осталяем чистый текст
        buffer = [x for x in buffer if x[:4] not in settings.EOW_KEY_CODES]
        
        if not self.upper_fix_required(buffer):
            return

        # ... иначе заменяем в каждом элементе буфера, кроме первого, признаки капса на нижний регистр
        buffer = [x[:3] + '00' for x in buffer]
        buffer[0] = buffer[0][:3] + '10'
        # self.buffer[-len(buffer):] = ['05700'] + buffer + ['05700']
        self.buffer = ['05700'] + buffer + ['05700']

        # добавляем в начало и конец по пробелу чтобы правильно 
        # обрабатывались нграммы начала слов (" ns " = " ты ")
        target_layout = self.get_target_layout(['05700'] + buffer + ['05700'])

        # если требуется конвертация раскладки буфера, то выходим из процедуры
        # конвертация раскладки буфера произойдет в kb_auto_process, а капсы мы уже исправили
        if target_layout != self.initial_layout:
            self.initial_layout = target_layout
            self.set_layout(target_layout)
            # return
        
        # возвращаем в конец буфера последнюю нажатую клавишу
        buffer.append(self.encode_key(key_code))

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
            
            # любой симовол окончания строки меняем на пробел
            if v[:4] in settings.EOW_KEY_CODES:
                string += ' '
                continue
            
            for k in EV_KEYS:

                # символ не из печатного множества
                if int(v[:3]) != k[5]:
                    continue

                # печатный символ + капс
                if v[3] != v[4] and usecaps:
                    string += k[2] if layout == 'us' else k[4]
                # печатный символ + некапс
                else:
                    string += k[1] if layout == 'us' else k[3]
                break

        return string
    
    def update_buffer(self, key_code):
        """"""
        if key_code == 14: # backspace            
            if self.buffer:
                self.buffer.pop()
            # если удалили всю строку в буфере, до добавляем метку начала строки
            self.buffer = ['00000'] if not self.buffer else self.buffer
            return
        
        # если зажат ctrl то обнуляем буфер и символ не добавляем
        if bool(set(self.keyboard.active_keys()) & set((29, 97))): # ctrl
            self.buffer = ['00000']
            return
        
        # видимый символ
        if key_code in VIS_KEYS:
            # это первый видимый символ после конца слова то обнуляем буфер
            if self.buffer[-1][:4] in settings.EOW_KEY_CODES:
                self.buffer = ['00000']
            # добавляем символ в буфер
            self.buffer.append(self.encode_key(key_code))
            return

        # любой другой невидимый символ, например: ctrl + z, стрелки        
        # но учитываем что буфер не обнуляют: 
        # - шифт не обнуляет буфер, т.к. может быть shift + видимый символ
        # - символ-признак автопереключения и или ручного переключения
        if (key_code not in (42, 54) and
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
        key_code = int(event.key_code)

        # KEY HOLD
        if (event.type == 'hold' and
            key_code not in (42, 54)): # shift
            self.buffer = ['00000']
            return

        # KEY DOWN
        if event.type == 'down':
            self.keyboard.press(key_code)
            self.update_buffer(key_code)

            if settings.SWITCH_TWOCAPS:
                self.caps_auto_process(key_code)
            if settings.SWITCH_MANUAL:
                self.kb_manual_process(key_code)
            if settings.SWITCH_AUTO:
                self.kb_auto_process(key_code)

        # KEY UP
        if event.type == 'up':
            self.keyboard.release(key_code)

            # обновляем текущую раскладку при ручном переключении
            if key_code in settings.SYS_SWITCH_KEY:
                self.initial_layout = self.get_layout()

    def start(self):
        """"""
        self.mouse.on_button_event(self.on_mouse_event)
        self.keyboard.on_key_event(self.on_keyboard_event)


switcher = Switcher()
switcher.start()
gtk.main()