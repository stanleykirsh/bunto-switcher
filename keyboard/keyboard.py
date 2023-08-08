from time import sleep
from time import time as TM
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

    controllers = []
    listeners = []
    devthreads = []
    devpaths = []

    _KEY_DELAY = 0.004      # sec 0.004
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
                # Stop working thread if exist.
                for devthread in self.devthreads:
                    if devthread:
                        self._TERMINATION_SIGN = True
                        devthread.join()
                        self._TERMINATION_SIGN = False
                self.controllers = []
                self.listeners = []
                self.devthreads = []
                self.devpaths = []
                # (Re)create main thread in any case.
                # If device configuration has been changed then it resets in every _GETDEVICE_DELAY seconds.
                for devpath in self._get_devices():
                    listener = InputDevice(devpath)
                    controller = UInput.from_device(devpath)
                    thread = Thread(
                        target=self._listener_loop, args=(callback, listener,))
                    thread.start()
                    self.listeners.append(listener)
                    self.controllers.append(controller)
                    self.devthreads.append(thread)
                sleep(self._GETDEVICE_DELAY)
            except Exception as e:
                print(f'Exception in keyboard _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATION_SIGN:
            try:
                for event in listener.read_loop():
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
        return devpaths

    def on_key_event(self, callback):
        """"""
        # Run main loop in its own thread for async work all the rest.
        thread = Thread(
            target=self._main_loop,
            args=(callback,),
            daemon=True)
        thread.start()

    def _call_async_and_await(self, func, args):
        threads = []
        for controller in self.controllers:
            args = args + (controller,)
            thread = Thread(
                target=func,
                args=args)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def _press(self, char: str, controller):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        controller.syn()
        sleep(self._KEY_DELAY)

    def _release(self, char: str, controller):
        """"""
        key_code = ecodes.ecodes[self._char_to_key(char)]
        controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        controller.syn()
        sleep(self._KEY_DELAY)

    def _send(self, chars: str, controller):
        """"""
        if chars == ' ':
            chars = 'space'

        chars = chars.split('+')
        for char in chars:
            self._press(char, controller)
        for char in reversed(chars):
            self._release(char, controller)

    def _write(self, text: str, controller):
        """"""
        for char in text:
            self._press(char, controller)
            self._release(char, controller)

    def _is_pressed(self, key_char, listener):
        """"""
        if self._char_to_code(key_char) in listener.active_keys(verbose=False):
            return True
        return False

    def _is_caps_locked(self, listener):
        """"""
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

    def press(self, char: str):
        """"""
        self._call_async_and_await(self._press, (char,))

    def release(self, char: str):
        """"""
        self._call_async_and_await(self._release, (char,))

    def send(self, chars: str):
        """"""
        self._call_async_and_await(self._send, (chars,))

    def write(self, text: str):
        """"""
        self._call_async_and_await(self._send, (text,))

    def is_pressed(self, key_char):
        """"""
        for listener in self.listeners:
            if self._is_pressed(key_char, listener):
                return True
        return False

    def is_caps_locked(self):
        """"""
        for listener in self.listeners:
            if self._is_caps_locked(listener):
                return True
        return False


### DEBUG ###
"""
def test(event):
    print(event)


k = Keyboard()
k.on_key_event(test)
input()
"""
# DEBUG ###
