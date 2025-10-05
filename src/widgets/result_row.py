# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .shared import *

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_row.ui')
class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'
  __gsignals__ = {
    'info-clicked': (GObject.SignalFlags.RUN_LAST, None, (Gtk.Widget,))
  }

  # Widgets
  label = Gtk.Template.Child()
  info_button = Gtk.Template.Child()

  # Properties
  digits = GObject.Property(type=int, default=0)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.info_button.connect('clicked', self.on_info_button)

  def on_info_button(self, button):
    self.emit('info-clicked', button)

  def set_result(self, result: float):
    if result is None:
      result = 'N/A'
    else:
      result = str(round(result, self.digits))
    self.label.set_label(result)

  def set_feedback(self, result: float, thresholds: list):
    if result is None:
      set_style(self, None)
      self.set_subtitle('')
      return
    thresholds.sort(key=lambda t: t.get('value'))
    thresholds.reverse()
    for threshold in thresholds:
      threshold_value = threshold.get('value')
      if result >= threshold_value:
        self.set_subtitle(threshold.get('text'))
        set_style(self, threshold.get('style'))
        break

  def set_digits(self, digits: int):
    self.digits = digits

  def get_digits(self) -> int:
    return self.digits
