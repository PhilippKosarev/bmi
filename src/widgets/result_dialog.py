# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .result_row import ResultRow
from .shared import *

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

def set_thresholds(self, thresholds: list):
  n_thresholds = len(thresholds)
  for i in range(n_thresholds):
    if i != 0:
      prev_threshold = thresholds[i-1]
    else:
      prev_threshold = None
    if i < n_thresholds - 1:
      next_threshold = thresholds[i+1]
    else:
      next_threshold = None
    threshold = thresholds[i]
    text = threshold.get('text')
    value = threshold.get('value')
    style = threshold.get('style')
    row = Adw.ActionRow()
    if prev_threshold is None:
      title = _("Under {}").format(next_threshold.get('value'))
    elif next_threshold is None:
      title = _("Over {}").format(value)
    else:
      title = _("From {} to {}").format(value, next_threshold.get('value'))
    row.set_title(title)
    row.set_subtitle(text)
    set_style(row, style)
    row.add_css_class('heading')
    self.thresholds_group.add(row)

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_dialog.ui')
class ResultDialog(Adw.Dialog):
  __gtype_name__ = 'ResultDialog'

  result_label = Gtk.Template.Child()
  feedback_label = Gtk.Template.Child()
  thresholds_group = Gtk.Template.Child()

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
    set_thresholds(self, thresholds)
