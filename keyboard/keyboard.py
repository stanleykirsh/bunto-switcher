import os
import logging

from time import sleep
from datetime import datetime
from threading import Thread, current_thread
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
    devices = None

    # sec 0.02, assumed 50Hz typical keyboard ratio # sinse GNOME 45 works
    # sinse GNOME 45 works instantly, so set to 0.0
    _KEY_DELAY = 0.0

    _GETDEVICE_DELAY = 10   # sec 10
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
                _devices = self._get_devices()

                # [Re]create main thread when devices was changed.
                # Stop working threads if exist. And create new ones.
                self._TERMINATION_SIGN = True
                for devthread in self.devthreads:
                    devthread.join()
                self._TERMINATION_SIGN = False

                self.listeners = []
                self.controllers = []
                self.devthreads = []

                for devid, devpath in enumerate(_devices):
                    # If no device is found, then without this condition the whole loop will fail 
                    # and threads for other valid devices will not be created again until the application is restarted. 
                    # Next condition helps to avoid hangs if the keyboard was disconnected and reconnected while the computer was asleep. 
                    if not os.path.exists(devpath):
                        continue
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

                self.devices = _devices
                sleep(self._GETDEVICE_DELAY)

            except Exception as e:
                self.devices = None
                logging.exception(f'{datetime.now()} Exception occurred')
                print(f'Exception in keyboard _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATION_SIGN:
            try:
                for event in listener.read_loop():
                    self.lastdevid = int(current_thread().name)
                    if not self.controllers:
                        continue
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
                self.devices = None
                logging.exception(f'{datetime.now()} Exception occurred')
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

    def press(self, key: int | str):
        """"""
        key_code = key
        if isinstance(key, str): key_code = ecodes.ecodes[self._char_to_key(key)]
        self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        self.controller.syn()

    def release(self, key: int | str):
        """"""
        key_code = key
        if isinstance(key, str): key_code = ecodes.ecodes[self._char_to_key(key)]
        self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        self.controller.syn()

    def send(self, keys: list[int] | list[str]):
        """"""
        # keys = keys.split('+')
        for key in keys:
            key_code = key
            if isinstance(key, str): key_code = ecodes.ecodes[self._char_to_key(key)]
            self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
            self.controller.syn()

        sleep(self._KEY_DELAY)
        for key in reversed(keys):
            key_code = key
            if isinstance(key, str): key_code = ecodes.ecodes[self._char_to_key(key)]
            self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
            self.controller.syn()

    def type(self, text: int | str | list):
        """"""
        for key in text:
            key_code = key          
            if isinstance(key, str): key_code = ecodes.ecodes[self._char_to_key(key)]
            self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
            self.controller.syn()
            self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
            self.controller.syn()

    def is_pressed(self, key: int | str):
        """"""        
        key_code = key
        listener = self.listeners[self.lastdevid]
        if isinstance(key, str): key_code = self._char_to_code(key)        
        if key_code in listener.active_keys(verbose=False):
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

    def _key_to_char(self, key_name: str):
        """"""
        for line in keymap.EV_KEYS:
            if line[0] == key_name:
                return line[1]

    def _char_to_key(self, char: str):
        """"""
        for line in keymap.EV_KEYS:
            if char.lower() in (line[1], line[3]):
                return line[0]

    def _char_to_code(self, char: str):
        """"""
        for line in keymap.EV_KEYS:
            if char.lower() in (line[1], line[3]):
                return line[5]

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
