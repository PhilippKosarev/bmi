# Imports
from gi.repository import Gtk, Adw

# Class
class GenderRow():
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Configuring row
    self.string_list = Gtk.StringList()
    for item in [_("Average"), _("Female"), _("Male")]:
      self.string_list.append(item)
    self.row = Adw.ComboRow()
    self.row.set_model(self.string_list)
    self.set_title(_("Gender"))
    self.row.connect('notify::selected-item', self.on_row_activated)
    # Object vars
    self.callback = None

  def set_title(self, text):
    self.row.set_title(text)

  def set_tooltip(self, text):
    self.row.set_tooltip_text(text)

  def get_value(self):
    return self.row.get_selected()

  def set_value(self, value):
    self.row.set_selected(value)

  def set_group(self, group):
    group.add(self.row)

  def get_name(self):
    return 'GenderRow'

  def set_callback(self, callback):
    self.callback = callback

  def on_row_activated(self, row, param):
    if self.callback is not None:
      self.callback(self)
