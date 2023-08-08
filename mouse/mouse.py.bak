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

    callback = None
    listener = None
    devpaths = []

    def __init__(self):
        """"""
        self._get_devices()

    def _get_devices(self):
        """"""
        for path in list_devices():
            listener = InputDevice(path)
            try:
                if (ecodes.BTN_MOUSE in listener.capabilities()[ecodes.EV_KEY]
                        and listener.name != 'py-evdev-uinput'):
                    print('обнаружено устройство типа мышь:', path)
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
                        ######################################
                        categorized = str(categorize(event))
                        if 'BTN_LEFT' in categorized:
                            callback(Event('272', 'BTN_LEFT', 'left button', categorized[-1]))
                        if 'BTN_MIDDLE' in categorized:
                            callback(Event('274', 'BTN_MIDDLE', 'middle button', categorized[-1]))
                        if 'BTN_RIGHT' in categorized:
                            callback(Event('273', 'BTN_RIGHT', 'right button', categorized[-1]))
            except Exception as e:
                print(e)
                self.listener = None
                sleep(5)
                pass

    def on_button_event(self, callback):
        for devpath in self.devpaths:
            thread = Thread(target=self._listener_loop, args=[
                            callback, devpath], daemon=True)
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
