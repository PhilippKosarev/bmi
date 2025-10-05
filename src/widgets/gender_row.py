# Imports
from gi.repository import Gtk, Adw
from enum import Enum

# Internal imports
from .dropdown_row import DropDownRow

# Class
class GenderRow(DropDownRow):
  __gtype_name__ = 'GenderRow'
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_size_request(260, 60)
    self.set_title(_("Gender"))
    self.string_list = Gtk.StringList()
    genders = [_("Average"), _("Female"), _("Male")]
    [self.string_list.append(gender) for gender in genders]
    self.set_model(self.string_list)

  def set_value(self, value: int):
    self.set_selected(value)

  def get_value(self):
    return self.get_selected()

  def get_signal(self):
    return 'notify::selected-item'

  def get_name(self):
    return self.__class__.__name__
