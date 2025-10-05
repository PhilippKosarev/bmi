# Imports
from gi.repository import Gtk, Adw, GObject

# Internal functions
# def on_icon_name_changed(self, param):
#   self.icon.set_from_icon_name(self.icon_name)
#   self.icon.set_visible(self.icon_name is not None)

class BaseRow(Adw.ActionRow):
  __gtype_name__ = 'BaseRow'

  key = GObject.Property(
    nick = 'key',
    blurb = "The object's key value",
    type = str,
  )
  # icon_name = GObject.Property(
  #   nick = 'icon-name',
  #   blurb = "The widget's icon",
  #   type = str,
  # )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # TODO: Uncomment this once AdwActionRow loses the icon-name property
    # self.icon = Gtk.Image(visible=False)
    # self.connect('notify::icon-name', on_icon_name_changed)
    # if isinstance(self, Adw.ActionRow):
    #   self.add_prefix(self.icon)

  def get_key(self) -> str:
    return self.key

  def set_key(self, key: str):
    self.key = key

  # def get_icon_name(self) -> str:
  #   return self.icon_name

  # def set_icon_name(self, icon_name: str):
  #   self.icon_name = icon_name
