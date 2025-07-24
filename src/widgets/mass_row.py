# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .spin_row import SpinRow

# Helper functions
def kg_to_lb(value): return value * 2.2046226218
def lb_to_kg(value): return value * 1 / kg_to_lb(1)

# Class
class MassRow(SpinRow):
  __gtype_name__ = 'MassRow'

  imperial = GObject.Property(
    type=bool, default=False,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_subtitle(_('Kilograms'))

  # def update_range(self):
  #   if self.imperial:
  #     lower = self.value_range.get('lower').get('imperial')
  #     upper = self.value_range.get('upper').get('imperial')
  #   else:
  #     lower = self.value_range.get('lower').get('metric')
  #     upper = self.value_range.get('upper').get('metric')
  #   self.row.set_range(lower, upper)

  # def set_range(self, lower, upper):
  #   self.value_range = {
  #     'lower': {'metric': lower, 'imperial': round(kg_to_lb(lower), 0)},
  #     'upper': {'metric': upper, 'imperial': round(kg_to_lb(upper), 0)},
  #   }
  #   self.update_range()

  def get_kilograms(self):
    if self.imperial:
      return lb_to_kg(self.get_value())
    else:
      return self.get_value()

  def get_pounds(self):
    if self.imperial:
      return self.get_value()
    else:
      return kg_to_lb(self.get_value())

  def set_imperial(self, imperial: bool):
    if self.imperial is imperial:
      return
    value = self.get_value()
    if imperial is True:
      value = kg_to_lb(value)
      self.set_subtitle(_('Pounds'))
    else:
      value = lb_to_kg(value)
      self.set_subtitle(_('Kilograms'))
    value = round(value, 0)
    self.imperial = imperial
    # self.update_range()
    self.set_value(value)
