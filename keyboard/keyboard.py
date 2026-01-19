import os
import logging

from time import sleep
from datetime import datetime
from threading import Thread, current_thread
from evdev import InputDevice, UInput, list_devices, ecodes, categorize
from . import keymap


class Event:

    def __init__(self, key_code: int, key_name: str, key_char: str, event_type: str):
        """"""
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Keyboard:

    def __init__(self):
        """"""
        self.listeners : list[InputDevice] = []
        self.controllers = []
        self.devthreads = []

        self.lastdevid = 0
        self.controller = None

        self._GETDEVICE_DELAY = 10   # sec 10
        self._EXCEPTION_DELAY = 1    # sec 5
        self._TERMINATE = False

        self.KEY_TO_CHAR = {x[0]: x[1] for x in keymap.EV_KEYS}        
        self.CHAR_TO_CODE = {x[1]: x[5] for x in keymap.EV_KEYS} | {x[3]: x[5] for x in keymap.EV_KEYS}
        # self.CHAR_TO_KEY = {x[1]: x[0] for x in keymap.EV_KEYS} | {x[3]: x[0] for x in keymap.EV_KEYS}

        _LOG_FILE = '/usr/share/bunto/error.log'
        logging.basicConfig(filename=_LOG_FILE, level=logging.DEBUG)

    def _main_loop(self, callback):
        """"""
        while True:
            try:
                _devices = self._get_devices()

                # [Re]create main thread when devices was changed.
                # Stop working threads if exist. And create new ones.
                self._TERMINATE = True
                for devthread in self.devthreads:
                    devthread.join()
                self._TERMINATE = False

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
                    self.grab(listener)
                    controller = UInput.from_device(devpath)
                    thread = Thread(
                        target=self._listener_loop,
                        args=(callback, listener,),
                        name=str(devid))
                    thread.start()
                    self.listeners.append(listener)
                    self.controllers.append(controller)
                    self.devthreads.append(thread)

                # self.grab()
                sleep(self._GETDEVICE_DELAY)

            except Exception as e:
                """if self.listeners:
                    for listener in self.listeners:
                        self.ungrab(listener)"""
                logging.exception(f'{datetime.now()} Exception occurred')
                print(f'Exception in keyboard _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATE:
            try:
                for event in listener.read_loop():
                    self.lastdevid = int(current_thread().name)
                    if self.controllers:
                        self.controller = self.controllers[self.lastdevid]
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event)).split()
                        callback(
                            Event(
                                key_code=categorized[4],
                                key_name=categorized[5][1:-2],
                                event_type=categorized[6],
                                key_char='' # self.KEY_TO_CHAR[key_name])
                            ))
            except Exception as e:
                """if self.listeners:
                    for listener in self.listeners:
                        self.ungrab(listener)"""
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
            except Exception as e:
                """if self.listeners:
                    for listener in self.listeners:
                        self.ungrab(listener) """
                # print(f'Exception in keyboard _get_devices: {e}')
                # Здесь sleep не нужен, он только замедляет обновление устройств.
                # Сюда приходим только когда InputDevice(path) не является валидным evdev устройством.
                # Но таких находится всего несколько штук. Быстро их пролетаем, создаем валидные 
                # и больше сюда не возвращаемся пока система не обновит список аппаратных устройств.
                # sleep(self._EXCEPTION_DELAY)   
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

    def press(self, key_code: int):
        """"""
        self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
        self.controller.syn()

    def release(self, key_code: int):
        """"""
        self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up
        self.controller.syn()

    def type(self, key_codes: list[int], delay_milliseconds:int = 0):
        """"""
        for key_code in key_codes:
            self.controller.write(ecodes.EV_KEY, key_code, 1)  # KEY_X down
            self.controller.syn()
            sleep(delay_milliseconds // 2)
            self.controller.write(ecodes.EV_KEY, key_code, 0)  # KEY_X up     
            self.controller.syn()
            sleep(delay_milliseconds // 2)

    def is_pressed(self, key_code: int) -> bool:
        """"""
        listener = self.listeners[self.lastdevid]
        return key_code in listener.active_keys(verbose=False)

    def is_caps_locked(self) -> bool:
        """"""
        listener = self.listeners[self.lastdevid]
        leds = listener.leds(verbose=True)
        for led in leds:
            if led[0] == 'LED_CAPSL' and led[1] == 1:
                return True
        return False

    def active_keys(self) -> list[int]:
        """"""
        if not self.listeners:
            return []
        listener = self.listeners[self.lastdevid]
        return listener.active_keys(verbose=False)

    def grab(self, device: InputDevice) -> None:
        """"""
        try:
            device.grab()
        except:
            pass

    def ungrab(self, device: InputDevice) -> None:
        """"""
        try:
            device.ungrab()
        except:
            pass
    
    """def grab(self) -> None:
        """"""
        self.listeners[self.lastdevid].grab()

    def ungrab(self) -> None:
        """"""
        self.listeners[self.lastdevid].ungrab()"""


### DEBUG ###
"""
def test(event):
    print(event)


k = Keyboard()
k.on_key_event(test)
input()
"""
# DEBUG ###
