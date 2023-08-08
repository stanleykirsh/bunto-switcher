from time import sleep
from threading import Thread
from evdev import InputDevice, ecodes, categorize, list_devices


class Event:

    def __init__(self, key_code, key_name, key_char, event_type):
        """ No comments. """
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Mouse:

    devthreads = []

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
                # Stop working threads if exist.
                for devthread in self.devthreads:
                    if devthread:
                        self._TERMINATION_SIGN = True
                        devthread.join()
                        self._TERMINATION_SIGN = False
                # (Re)create main thread in any case.
                # If device configuration has been changed then it resets in every _GETDEVICE_DELAY seconds.
                for devpath in self._get_devices():
                    listener = InputDevice(devpath)
                    thread = Thread(
                        target=self._listener_loop, args=(callback, listener,))
                    thread.start()
                    self.devthreads.append(thread)
                sleep(self._GETDEVICE_DELAY)
            except Exception as e:
                print(f'Exception in mouse _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATION_SIGN:
            try:
                for event in listener.read_loop():
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event))
                        if 'BTN_LEFT' in categorized and 'down' in categorized:
                            callback(Event('272', 'BTN_LEFT',
                                     'left button', categorized[-1]))
                        if 'BTN_MIDDLE' in categorized and 'down' in categorized:
                            callback(Event('274', 'BTN_MIDDLE',
                                     'middle button', categorized[-1]))
                        if 'BTN_RIGHT' in categorized and 'down' in categorized:
                            callback(Event('273', 'BTN_RIGHT',
                                     'right button', categorized[-1]))
            except Exception as e:
                print(f'Exception in mouse _listener_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _get_devices(self):
        """"""
        devpaths = []
        for path in list_devices():
            try:
                listener = InputDevice(path)
                if (ecodes.BTN_MOUSE in listener.capabilities()[ecodes.EV_KEY]
                        and listener.name != 'py-evdev-uinput'):
                    print('обнаружено устройство типа мышь:', path)
                    devpaths.append(listener.path)
            except:
                pass
        return devpaths

    def on_button_event(self, callback):
        """"""
        # Run main loop in its own thread for async work all the rest.
        thread = Thread(
            target=self._main_loop,
            args=(callback,),
            daemon=True)
        thread.start()


### DEBUG ###
'''
def test(event):
    print(event)

m = Mouse()
m.on_button_event(test)
input()
'''
# DEBUG ###
