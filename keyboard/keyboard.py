from time import sleep
from threading import Thread
from evdev import InputDevice, UInput, list_devices, ecodes, categorize
from . import keymap


class Event:
    def __init__(self, key_code, key_name, key_char, event_type):
        """ No comments. """
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Keyboard:

    callback = None
    controller = None
    listener = None
    devpaths = []

    def __init__(self):
        """"""
        self._get_devices()

    def _get_devices(self):
        """"""
        for path in list_devices():
            try:
                listener = InputDevice(path)
                if (ecodes.KEY_BACKSPACE in listener.capabilities()[ecodes.EV_KEY]
                        and listener.name != 'py-evdev-uinput'):
                    print('обнаружено устройство типа клавиатура:', path)
                    self.devpaths.append(listener.path)
            except:
                pass

    def _listener_loop(self, callback, devpath):
        """"""
        while True:
            try:
                ##############################################
                if not self.listener:
                    listener = InputDevice(devpath)
                else:
                    listener = self.listener
                ##############################################
                for event in listener.read_loop():
                    if event.type == ecodes.EV_KEY:
                        ######################################
                        if not self.listener:
                            self.listener = InputDevice(devpath)
                        if not self.controller:
                            self.controller = UInput.from_device(devpath)
                        ######################################
                        categorized = str(categorize(event)).split()
                        key_code = categorized[4]
                        key_name = categorized[5][1:-2]
                        key_char = self._key_to_char(key_name)
                        event_type = categorized[6]
                        callback(
                            Event(key_code, key_name, key_char, event_type))
            except Exception as e:
                print(e)
                self.listener = None
                sleep(5)
                pass

    def syn(self):
        self.controller.syn()

    def press(self, char):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        # self.controller.syn()

    def release(self, char):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        # self.controller.syn()

    def send(self, chars):
        """"""
        if chars == ' ':
            chars = 'space'

        chars = chars.split('+')
        for char in chars:
            self.press(char)
        for char in reversed(chars):
            self.release(char)

    def write(self, text):
        """"""
        for char in text:
            self.send(char)

    def is_pressed(self, key_char):
        """"""
        if self._char_to_code(key_char) in self.listener.active_keys(verbose=False):
            return True
        return False

    def _key_to_char(self, key_name):
        """"""
        for line in keymap.EV_KEYS:
            if line[0] == key_name:
                return line[1]

    def _char_to_key(self, char):
        """"""
        for line in keymap.EV_KEYS:
            if line[1] == char.lower() or line[2] == char:
                return line[0]

    def _char_to_code(self, char):
        """"""
        for line in keymap.EV_KEYS:
            if line[1] == char.lower():
                return line[3]

    def on_key_event(self, callback):
        """"""
        for devpath in self.devpaths:
            # создаем потоки с листенерами
            thread = Thread(target=self._listener_loop, args=[
                            callback, devpath], daemon=True)
            thread.start()


### DEBUG ###
'''
def test(event):
    print(event)


k = Keyboard()
k.on_key_event(test)
input()
'''
# DEBUG ###
