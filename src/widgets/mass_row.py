# Imports
from gi.repository import Gtk, Adw

# Helper functions
def kg_to_lb(value): return value * 2.2046226218
def lb_to_kg(value): return value * 1 / kg_to_lb(1)

# Class
class MassRow():
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
    self.row.set_subtitle(_('Kilograms'))
    self.row.connect('output', self.on_value_changed)
    # Object vars
    self.callback = None

  def set_group(self, group):
    group.add(self.row)

  def set_title(self, title):
    self.row.set_title(title)

  def set_tooltip(self, text):
    self.row.set_tooltip_text(text)

  def set_value(self, value):
    self.row.set_value(value)

  def get_value(self):
    value = self.row.get_value()
    if self.imperial is True:
      value = lb_to_kg(value)
    return value

  def update_range(self):
    if self.imperial:
      lower = self.value_range.get('lower').get('imperial')
      upper = self.value_range.get('upper').get('imperial')
    else:
      lower = self.value_range.get('lower').get('metric')
      upper = self.value_range.get('upper').get('metric')
    self.row.set_range(lower, upper)

  def set_range(self, lower, upper):
    self.value_range = {
      'lower': {'metric': lower, 'imperial': round(kg_to_lb(lower), 0)},
      'upper': {'metric': upper, 'imperial': round(kg_to_lb(upper), 0)},
    }
    self.update_range()

  def set_imperial(self, imperial: bool):
    if self.imperial is imperial:
      return
    value = self.row.get_value()
    if imperial is True:
      value = kg_to_lb(value)
      self.row.set_subtitle(_('Pounds'))
    else:
      value = lb_to_kg(value)
      self.row.set_subtitle(_('Kilograms'))
    value = round(value, 0)
    self.imperial = imperial
    self.update_range()
    self.set_value(value)

  def set_callback(self, callback):
    self.callback = callback

  def on_value_changed(self, row):
    if self.callback is not None:
      self.callback(self)

  def get_name(self):
    return 'MassRow'
