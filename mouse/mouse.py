from threading import Thread
from evdev import InputDevice, ecodes, categorize


class Event:
    def __init__(self, key_code, key_name, key_char, event_type):
        """ No comments. """
        self.key_code = key_code
        self.key_name = key_name
        self.key_char = key_char
        self.type = event_type


class Mouse:
    # TBD : автоопределение устройства мыши
    device_path = '/dev/input/event6'
    listener = InputDevice(device_path)
    callback = None

    def __init__(self):
        """"""
        pass

    def _on_button(self, callback):
        while True:
            try:
                self.listener = InputDevice(self.device_path)
                for event in self.listener.read_loop():
                    if event.type == ecodes.EV_KEY:
                        categorized = str(categorize(event))
                        if 'BTN_LEFT' in categorized:
                            callback(
                                Event(
                                    '272',
                                    'BTN_LEFT',
                                    'left button',
                                    categorized[-1]))
                        if 'BTN_MIDDLE' in categorized:
                            callback(
                                Event(
                                    '274',
                                    'BTN_MIDDLE',
                                    'middle button',
                                    categorized[-1]))
                        if 'BTN_RIGHT' in categorized:
                            callback(
                                Event(
                                    '273',
                                    'BTN_RIGHT',
                                    'right button',
                                    categorized[-1]))
            except:
                pass

    def on_button(self, callback):
        thread = Thread(target=self._on_button, args=[callback], daemon=True)
        thread.start()
