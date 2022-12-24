from . import keymap
from evdev import InputDevice, UInput, list_devices, ecodes, categorize


class Event:
    def __init__(self, key_code, key_name, key_char, event_type):
        """ No comments. """
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Keyboard:

    device_path = None
    controller = None
    listener = None

    def __init__(self):
        """"""
        self.device_path = self._get_device_path()
        self.controller = UInput.from_device(self.device_path)

    def _get_device_path(self):
        """"""
        for path in list_devices():
            listener = InputDevice(path)
            try:
                if (ecodes.KEY_BACKSPACE in listener.capabilities()[ecodes.EV_KEY]
                        and listener.name != 'py-evdev-uinput'):
                    print('keyboard detected on path:', path)
                    return listener.path
            except:
                pass

    def read_event(self):
        """"""
        while True:
            try:
                self.listener = InputDevice(self.device_path)
                for event in self.listener.read_loop():
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event)).split()
                        key_code = categorized[4]
                        key_name = categorized[5][1:-2]
                        key_char = self._key_to_char(key_name)
                        event_type = categorized[6]
                        return Event(key_code, key_name, key_char, event_type)
            except:
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
