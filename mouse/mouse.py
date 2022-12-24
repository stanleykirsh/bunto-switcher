import io

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
    device_path = None

    def __init__(self):
        """"""
        self.device_path = self._get_device_path()

    def _get_device_path(self):
        """"""
        for path in list_devices():
            listener = InputDevice(path)
            capabilities = _print_to_string(listener.capabilities(verbose=True))
            if 'BTN_MOUSE' in capabilities and listener.name != 'py-evdev-uinput':
                print('mouse detected on path:', path)
                return path

    def _on_button(self, callback):
        while True:
            try:
                self.listener = InputDevice(self.device_path)
                for event in self.listener.read_loop():
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event))
                        if 'BTN_LEFT' in categorized:
                            callback(Event('272', 'BTN_LEFT',
                                     'left button', categorized[-1]))
                        if 'BTN_MIDDLE' in categorized:
                            callback(Event('274', 'BTN_MIDDLE',
                                     'middle button', categorized[-1]))
                        if 'BTN_RIGHT' in categorized:
                            callback(Event('273', 'BTN_RIGHT',
                                     'right button', categorized[-1]))
            except:
                pass

    def on_button(self, callback):
        thread = Thread(target=self._on_button, args=[callback], daemon=True)
        thread.start()


def _print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents
