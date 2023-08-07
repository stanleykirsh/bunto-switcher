from time import sleep
from threading import Thread
from evdev import InputDevice, UInput, list_devices, ecodes, categorize
from . import keymap

class Event:
    
    def __init__(self, key_code: str, key_name: str, key_char: str, event_type: str):
        """"""
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type

class Keyboard:

    controller = None
    listener = None
    devpath = None
    devthread = None

    _KEY_DELAY = 0.005      # sec 0.005
    _GETDEVICE_DELAY = 30   # sec 30
    _EXCEPTION_DELAY = 5    # sec 5
    _TERMINATION_SIGN = False

    def __init__(self):
        """"""
        pass

    def _main_loop(self, callback):  
        """"""
        while True:
            try:                
                # Stop main thread if exist.
                if self.devthread:
                    self._TERMINATION_SIGN = True
                    self.devthread.join()
                    self._TERMINATION_SIGN = False
                # (Re)create main thread in any case. 
                # If device configuration has been changed then it resets in every _GETDEVICE_DELAY seconds.
                self.devpath = self._get_devices()
                self.listener = InputDevice(self.devpath)
                self.controller = UInput.from_device(self.devpath)
                self.devthread = Thread(target=self._listener_loop, args=(callback,))
                self.devthread.start()
                sleep(self._GETDEVICE_DELAY)
            except Exception as e:
                print(f'Exception in _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)            

    def _listener_loop(self, callback):
        """"""
        while not self._TERMINATION_SIGN:
            try:
                for event in self.listener.read_loop():
                    if event.type == ecodes.EV_KEY:                        
                        categorized = str(categorize(event)).split()
                        key_code = categorized[4]
                        key_name = categorized[5][1:-2]
                        key_char = self._key_to_char(key_name)
                        event_type = categorized[6]
                        callback(
                            Event(key_code, key_name, key_char, event_type))
            except Exception as e:
                print(f'Exception in _listener_loop: {e}')   
                sleep(self._EXCEPTION_DELAY)

    def _get_devices(self):
        """"""
        devpaths = []
        for path in list_devices():
            try:
                listener = InputDevice(path)
                if (ecodes.KEY_BACKSPACE in listener.capabilities()[ecodes.EV_KEY]
                        and listener.name != 'py-evdev-uinput'):
                    print('обнаружено устройство типа клавиатура:', path)
                    devpaths.append(listener.path)
            except Exception as e:
                pass 
        return devpaths[0]

    def on_key_event(self, callback):
        """"""
        thread = Thread(
            target=self._main_loop,
            args=(callback,),
            daemon=True)
        thread.start()

    def press(self, char: str):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        self.controller.syn()
        sleep(self._KEY_DELAY)

    def release(self, char: str):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        self.controller.syn()
        sleep(self._KEY_DELAY)

    def send(self, chars: str):
        """"""
        if chars == ' ':
            chars = 'space'

        chars = chars.split('+')
        for char in chars:
            self.press(char)
        for char in reversed(chars):
            self.release(char)

    def write(self, text: str):
        """"""
        for char in text:
            self.press(char)
            self.release(char)

    def is_pressed(self, key_char):
        """"""
        if self._char_to_code(key_char) in self.listener.active_keys(verbose=False):
            return True
        return False

    def is_caps_locked(self):
        """"""
        leds = self.listener.leds(verbose=True)
        for led in leds:
            if led[0] == 'LED_CAPSL' and led[1] == 1:
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

### DEBUG ###
"""
def test(event):
    print(event)


k = Keyboard()
k.on_key_event(test)
input()
"""
# DEBUG ###
