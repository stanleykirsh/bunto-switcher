from gi.repository import Gtk, Gdk


class Clipboard:

    storage_text = None
    storage_image = None

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def __init__(self):
        """"""
        # Warm-up on init to prevent freeze in first restore
        self.save()
        self.restore()

    def clear(self):
        """"""
        self.clipboard.clear()

    def set_text(self, text: str):
        """"""
        self.clipboard.clear()
        self.clipboard.set_text(text, -1)
        Gtk.Clipboard.wait_is_text_available(self.clipboard)

    def set_image(self, pixbuf):
        """"""
        self.clipboard.clear()
        self.clipboard.set_image(pixbuf)
        Gtk.Clipboard.wait_is_image_available(self.clipboard)

    def get_text(self):
        """"""
        return Gtk.Clipboard.wait_for_text(self.clipboard)

    def get_image(self):
        """"""
        return Gtk.Clipboard.wait_for_image(self.clipboard)

    def save(self):
        """"""
        self.storage_text = self.get_text()
        self.storage_image = self.get_image()

    def restore(self):
        """"""
        if self.storage_text:
            self.set_text(self.storage_text)

        if self.storage_image:
            self.set_image(self.storage_image)

        self.storage_text = None
        self.storage_image = None
