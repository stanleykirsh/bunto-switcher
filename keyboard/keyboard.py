import logging

from time import sleep
from datetime import datetime
from threading import Thread, currentThread
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

    listeners = []
    controllers = []
    devthreads = []

    lastdevid = 0
    controller = None

    _KEY_DELAY = 0.02       # sec 0.02, assumed 50Hz typical keyboard ratio
    _GETDEVICE_DELAY = 30   # sec 30
    _EXCEPTION_DELAY = 5    # sec 5
    _TERMINATION_SIGN = False

    _LOG_FILE = '/usr/share/bunto/error.log'
    logging.basicConfig(filename=_LOG_FILE, level=logging.DEBUG)

    def __init__(self):
        """"""
        pass

    def _main_loop(self, callback):
        """"""
        while True:
            try:
                # Stop working thread if exist.
                self._TERMINATION_SIGN = True
                for devthread in self.devthreads:
                    devthread.join()
                self._TERMINATION_SIGN = False

                self.listeners = []
                self.controllers = []
                self.devthreads = []

                # (Re)create main thread in any case.
                # If device configuration has been changed then it resets in every _GETDEVICE_DELAY seconds.
                for devid, devpath in enumerate(self._get_devices()):
                    listener = InputDevice(devpath)
                    controller = UInput.from_device(devpath)
                    thread = Thread(
                        target=self._listener_loop,
                        args=(callback, listener,),
                        name=str(devid))
                    thread.start()
                    self.listeners.append(listener)
                    self.controllers.append(controller)
                    self.devthreads.append(thread)
                sleep(self._GETDEVICE_DELAY)

            except Exception as e:
                print(f'Exception in keyboard _main_loop: {e}')
                logging.exception(f'{datetime.now()} Exception occurred')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATION_SIGN:
            try:
                for event in listener.read_loop():
                    self.lastdevid = int(currentThread().name)
                    self.controller = self.controllers[self.lastdevid]
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event)).split()
                        key_code = categorized[4]
                        key_name = categorized[5][1:-2]
                        key_char = self._key_to_char(key_name)
                        event_type = categorized[6]
                        callback(
                            Event(key_code, key_name, key_char, event_type))
            except Exception as e:
                print(f'Exception in keyboard _listener_loop: {e}')
                logging.exception(f'{datetime.now()} Exception occurred')
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
            except Exception as _:
                pass
        return devpaths

    def on_key_event(self, callback):
        """"""
        # Run main loop in its own thread to able async work for all the rest.
        thread = Thread(
            target=self._main_loop,
            args=(callback,),
            daemon=True)
        thread.start()

    def press(self, char: str, duration: float = 0):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        self.controller.syn()
        sleep(duration)

    def release(self, char: str, duration: float = 0):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        self.controller.syn()
        sleep(duration)

    def send(self, chars: str | list):
        """"""
        if chars == ' ':
            chars = 'space'

        chars = chars.split('+')
        for char in chars:
            self.press(char)

        sleep(self._KEY_DELAY)
        for char in reversed(chars):
            self.release(char)

    def type(self, text: str | list):
        """"""
        for char in text:
            self.press(char)
            sleep(self._KEY_DELAY)
            self.release(char)
            sleep(self._KEY_DELAY)

    def is_pressed(self, key_char):
        """"""
        listener = self.listeners[self.lastdevid]
        if self._char_to_code(key_char) in listener.active_keys(verbose=False):
            return True
        return False

    def is_caps_locked(self):
        """"""
        listener = self.listeners[self.lastdevid]
        leds = listener.leds(verbose=True)
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

    def grab(self):
        """"""
        listener = self.listeners[self.lastdevid]
        listener.grab()
        pass

    def ungrab(self):
        """"""
        listener = self.listeners[self.lastdevid]
        listener.ungrab()
        pass


### DEBUG ###
"""
def test(event):
    print(event)


k = Keyboard()
k.on_key_event(test)
input()
"""
# DEBUG ###
