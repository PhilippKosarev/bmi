# Imports
from gi.repository import Gtk, Adw

# Helper functions
def in_to_cm(value): return value * 2.54
def cm_to_in(value): return value * (1 / in_to_cm(1))

# Class
class DistanceRow():
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Configuring row
    self.adjustment = Gtk.Adjustment(step_increment=1, page_increment=10)
    self.row = Adw.SpinRow.new(self.adjustment, 1, 1)
    self.row.set_size_request(270, 60)
    self.imperial = False
    self.value_range = {
      'lower': {'metric': 0, 'imperial': 0},
      'upper': {'metric': 0, 'imperial': 0},
    }
    self.row.set_subtitle(_('Centimetres'))
    self.row.connect('output', self.on_value_changed)
    # Object vars
    self.callback = None

  def set_group(self, group):
    group.add(self.row)

  def set_title(self, title):
    self.row.set_title(title)

  def set_tooltip(self, text):
    self.row.set_tooltip_text(text)

  def get_value(self):
    value = self.row.get_value()
    if self.imperial is True:
      value = in_to_cm(value)
    return value

  def set_value(self, value):
    self.row.set_value(value)

  def get_range(self):
    return self.value_range

  def set_range(self, lower, upper):
    self.value_range = {
      'lower': {'metric': lower, 'imperial': round(cm_to_in(lower), 0)},
      'upper': {'metric': upper, 'imperial': round(cm_to_in(upper), 0)},
    }
    self.update_range()


  def get_imperial(self):
    return self.imperial

  def set_imperial(self, imperial: bool):
    # Checking if value changed
    if self.imperial is imperial:
      return
    # Switching units
    value = self.row.get_value()
    if imperial is True:
      value = cm_to_in(value)
      self.row.set_subtitle(_('Inches'))
    else:
      value = in_to_cm(value)
      self.row.set_subtitle(_('Centimetres'))
    value = round(value, 0)
    self.imperial = imperial
    self.update_range()
    self.row.set_value(value)


  def update_range(self):
    if self.imperial:
      lower = self.value_range.get('lower').get('imperial')
      upper = self.value_range.get('upper').get('imperial')
    else:
      lower = self.value_range.get('lower').get('metric')
      upper = self.value_range.get('upper').get('metric')
    self.row.set_range(lower, upper)

  def set_callback(self, callback):
    self.callback = callback

  def on_value_changed(self, row):
    if self.callback is not None:
      self.callback(self)

  def get_name(self):
    return 'DistanceRow'
