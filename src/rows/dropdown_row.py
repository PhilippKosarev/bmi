# Imports
from gi.repository import Gtk, Adw, Gio, GObject

# Internal imports
from .base_row import BaseRow

# Shorthands vars
center = Gtk.Align.CENTER

class DropDownRow(Adw.ComboRow):
  __gtype_name__ = 'DropDownRow'

  key = GObject.Property(
    nick = 'key',
    blurb = "The object's key value",
    type = str,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.get_value = self.get_selected
    self.set_value = self.set_selected

  def get_key(self) -> str:
    return self.key

  def set_key(self, key: str):
    self.key = key

  def get_signal(self):
    return 'notify::selected'
