# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .spin_row import SpinRow
from .shared import *

# Class
class DistanceRow(SpinRow):
  __gtype_name__ = 'DistanceRow'

  imperial = GObject.Property(
    type=bool, default=False,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_subtitle(_('Centimetres'))

  def get_centimetres(self):
    value = self.get_value()
    if self.imperial:
      return in_to_cm(value)
    else:
      return value

  def get_inches(self):
    value = self.get_value()
    if self.imperial:
      return value
    else:
      return cm_to_in(value)

  def set_imperial(self, imperial: bool):
    if imperial == self.imperial:
      return
    self.imperial = imperial
    value = self.get_value()
    if imperial is True:
      value = cm_to_in(value)
      self.set_subtitle(_('Inches'))
    else:
      value = in_to_cm(value)
      self.set_subtitle(_('Centimetres'))
    value = round(value, 0)
    self.set_value(value)
