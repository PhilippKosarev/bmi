# Imports
from gi.repository import Gtk, Adw

# Class
class TimeRow():
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Configuring row
    self.adjustment = Gtk.Adjustment(step_increment=1, page_increment=10)
    self.row = Adw.SpinRow.new(self.adjustment, 1, 0)
    self.row.set_subtitle(_('Years'))
    self.row.connect('output', self.on_value_changed)
    # Object vars
    self.callback = None

  def set_title(self, text):
    self.row.set_title(text)

  def set_tooltip(self, text):
    self.row.set_tooltip_text(text)

  def get_value(self):
    return self.row.get_value()

  def set_value(self, value):
    return self.row.set_value(value)

  def get_range(self):
    lower = self.row.get_lower()
    upper = self.row.get_upper()
    return lower, upper

  def set_range(self, lower, upper):
    self.row.set_range(lower, upper)

  def set_group(self, group):
    group.add(self.row)

  def get_name(self):
    return 'TimeRow'

  def set_callback(self, callback):
    self.callback = callback

  def on_value_changed(self, row):
    if self.callback is not None:
      self.callback(self)
