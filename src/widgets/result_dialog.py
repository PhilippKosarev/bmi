# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .result_row import ResultRow
from .shared import *

# Helper functions
def stround(value: float) -> str:
  return str(round(value, 1))

class ThresholdRow(Adw.ActionRow):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.add_css_class('heading')
    self.prev_value = 0
    self.curr_value = 0
    self.next_value = 0
    self.units = ''

  def set_values(
    self,
    prev_value: float or None,
    curr_value: float,
    next_value: float or None,
  ):
    self.prev_value = prev_value
    self.curr_value = curr_value
    self.next_value = next_value
    self.update_title()

  def set_units(self, units: str):
    self.units = units
    self.update_title()

  def set_style(self, style):
    set_style(self, style)

  def update_title(self):
    if self.prev_value is None:
      title = _("Under {}").format(stround(self.next_value) + self.units)
    elif self.next_value is None:
      title = _("Over {}").format(stround(self.curr_value) + self.units)
    else:
      title = _("From {} to {}").format(
        stround(self.curr_value) + self.units,
        stround(self.next_value) + self.units,
      )
    self.set_title(title)

def thresholds_to_rows(thresholds: list, units: str = '') -> list:
  thresholds.sort(key=lambda x: x.get('value'))
  n_thresholds = len(thresholds)
  rows = []
  for i in range(n_thresholds):
    curr_threshold = thresholds[i]
    text = curr_threshold.get('text')
    style = curr_threshold.get('style')
    curr_value = curr_threshold.get('value')
    if i != 0:
      prev_value = thresholds[i-1].get('value')
    else:
      prev_value = None
    if i < n_thresholds - 1:
      next_value = thresholds[i+1].get('value')
    else:
      next_value = None
    row = ThresholdRow()
    row.set_values(prev_value, curr_value, next_value)
    row.set_style(style)
    row.set_subtitle(text)
    row.set_units(units)
    rows.append(row)
  return rows

# Internal functions
def set_labels(self, result: float, thresholds: list):
  for threshold in reversed(thresholds):
    threshold_value = threshold.get('value')
    if result >= threshold_value:
      self.feedback_label.set_label(threshold.get('text'))
      style = threshold.get('style')
      set_style(self.result_label, style)
      set_style(self.feedback_label, style)
      break

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_dialog.ui')
class ResultDialog(Adw.Dialog):
  __gtype_name__ = 'ResultDialog'

  result_label = Gtk.Template.Child()
  feedback_label = Gtk.Template.Child()
  thresholds_group = Gtk.Template.Child()
  context_group = Gtk.Template.Child()

  def __init__(self, result_row: ResultRow, **kwargs):
    super().__init__(**kwargs)
    title = result_row.get_title()
    self.set_title(title)
    self.digits = result_row.get_digits()

  def set_result(self, result: float):
    result = str(round(result, self.digits))
    self.result_label.set_label(result)

  def set_feedback(self, result: float, thresholds: list):
    thresholds.sort(key=lambda t: t.get('value'))
    set_labels(self, result, thresholds)
    rows = thresholds_to_rows(thresholds)
    for row in rows:
      self.thresholds_group.add(row)

  def set_context(self, description: str, thresholds: list, imperial: bool):
    if imperial:
      units = _("lb")
      for i in range(len(thresholds)):
        threshold = thresholds[i]
        value = threshold.get('value')
        thresholds[i]['value'] = kg_to_lb(value)
    else:
      units = _("kg")
    rows = thresholds_to_rows(thresholds, units)
    for row in rows:
      self.context_group.add(row)
    self.context_group.set_description(description)
    self.context_group.set_visible(True)
