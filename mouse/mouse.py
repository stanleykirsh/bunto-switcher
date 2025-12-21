from time import sleep
from threading import Thread, current_thread
from evdev import InputDevice, ecodes, categorize, list_devices


class Event:

    def __init__(self, key_code, key_name, key_char, event_type):
        """ No comments. """
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Mouse:

    def __init__(self):
        """"""
        self.listeners = []
        self.devthreads = []
        self.lastdevid = 0

        self._GETDEVICE_DELAY = 30   # sec 30
        self._EXCEPTION_DELAY = 5    # sec 5
        self._TERMINATE = False

    def _main_loop(self, callback):
        """"""
        while True:
            try:
                # Stop working thread if exist.
                self._TERMINATE = True
                for devthread in self.devthreads:
                    devthread.join()
                self._TERMINATE = False

                self.listeners = []
                self.devthreads = []

                # Recreate device threads every _GETDEVICE_DELAY seconds.
                for devid, devpath in enumerate(self._get_devices()):
                    listener = InputDevice(devpath)
                    thread = Thread(
                        target=self._listener_loop,
                        args=(callback, listener,),
                        name=str(devid))
                    thread.start()
                    self.listeners.append(listener)
                    self.devthreads.append(thread)
                sleep(self._GETDEVICE_DELAY)

            except Exception as e:
                print(f'Exception in mouse _main_loop: {e}')
                sleep(self._EXCEPTION_DELAY)

    def _listener_loop(self, callback, listener):
        """"""
        while not self._TERMINATE:
            try:
                for event in listener.read_loop():
                    self.lastdevid = int(current_thread().name)
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event))
                        if 'BTN_LEFT' in categorized and 'down' in categorized:
                            callback(Event('272', 'BTN_LEFT', 'left button', categorized[-1]))
                        if 'BTN_MIDDLE' in categorized and 'down' in categorized:
                            callback(Event('274', 'BTN_MIDDLE', 'middle button', categorized[-1]))
                        if 'BTN_RIGHT' in categorized and 'down' in categorized:
                            callback(Event('273', 'BTN_RIGHT', 'right button', categorized[-1]))
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
