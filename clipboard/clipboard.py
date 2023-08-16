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

    def set_text(self, text):
        """"""
        self.clipboard.set_text(text, -1)

    def set_image(self, pixbuf):
        """"""
        self.clipboard.set_image(pixbuf)  

    def get_text(self):
        """"""
        pass

    def get_image(self):
        """"""
        pass

    def save(self):
        """"""
        self.storage_text = Gtk.Clipboard.wait_for_text(self.clipboard)
        self.storage_image = Gtk.Clipboard.wait_for_image(self.clipboard)

    def restore(self):
        """"""
        if self.storage_text:
            self.set_text(self.storage_text)
        if self.storage_image:
            self.set_image(self.storage_image)
      