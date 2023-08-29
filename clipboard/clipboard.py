import time
from gi.repository import Gtk, Gdk


class Clipboard:

    storage_text = None
    storage_image = None

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def __init__(self):
        """"""
        pass

    def clear(self):
        """"""
        self.clipboard.clear()
        for _ in range(100):
            if not Gtk.Clipboard.wait_is_text_available(self.clipboard):
                if not Gtk.Clipboard.wait_is_image_available(self.clipboard):
                    return
            time.sleep(0.01)

    def set_text(self, text: str):
        """"""
        self.clear()
        self.clipboard.set_text(text, -1)
        for _ in range(100):
            if Gtk.Clipboard.wait_is_text_available(self.clipboard):
                return
            time.sleep(0.01)

    def set_image(self, pixbuf):
        """"""
        self.clear()
        self.clipboard.set_image(pixbuf)
        for _ in range(100):
            if Gtk.Clipboard.wait_is_image_available(self.clipboard):
                return
            time.sleep(0.01)

    def get_text(self):
        """"""
        if Gtk.Clipboard.wait_is_text_available(self.clipboard):
            return Gtk.Clipboard.wait_for_text(self.clipboard)
        return None

    def get_image(self):
        """"""
        if Gtk.Clipboard.wait_is_image_available(self.clipboard):
            return Gtk.Clipboard.wait_for_image(self.clipboard)
        return None

    def save(self):
        """"""
        self.storage_text = self.get_text()
        self.storage_image = self.get_image()

    def restore(self):
        """"""
        if self.storage_text:
            self.set_text(self.storage_text)
        else:
            self.set_text('')

        if self.storage_image:
            self.set_image(self.storage_image)
        else:
            pass

        self.storage_text = None
        self.storage_image = None
