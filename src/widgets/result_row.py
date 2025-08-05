# Imports
from gi.repository import GObject, Gtk, Adw

# Helper functions
def clear_styles(widget):
  widget.remove_css_class("light-blue")
  widget.remove_css_class("success")
  widget.remove_css_class("warning")
  widget.remove_css_class("error")

def num_to_css(style):
  if style is None:
    return None
  if style == 0:   return 'light-blue'
  elif style == 1: return 'success'
  elif style == 2: return 'warning'
  elif style == 3: return 'error'
  else:
    print(f"Unhandled style '{style}'")
    exit(-1)

def set_style(widget, style):
  clear_styles(widget)
  if style is None:
    return None
  style = num_to_css(style)
  widget.add_css_class(style)

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_row.ui')
class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'

  # Important widgets
  label = Gtk.Template.Child()
  info_button = Gtk.Template.Child()
  info_dialog = Gtk.Template.Child()
  info_page = Gtk.Template.Child()
  thresholds_group = Gtk.Template.Child()
  # Properties
  digits = GObject.Property(type=int, default=0)
  rows = []
  thresholds = []
  calc_func = None

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.connect('activated', self.on_row_clicked)
    self.info_button.connect('clicked', self.on_info_button)
    self.callback = None

  def set_feedback(self, subtitle: str):
    self.set_subtitle(subtitle)

  def set_thresholds(self, thresholds: list):
    self.thresholds = thresholds

  def set_calc_func(self, calc_func: callable):
    self.calc_func = calc_func

  def update(self, inputs: dict):
    # print(self.calc_func)
    if self.calc_func is not None:
      result = self.calc_func(inputs)
    else:
      result = 'N/A'
    if type(result) is str:
      self.label.set_label(result)
      self.set_feedback('')
      set_style(self, None)
      self.info_button.set_visible(False)
      return
    self.info_button.set_visible(True)
    result_text = str(round(result, self.digits))
    self.label.set_label(result_text)
    self.update_feedback(inputs, result)

  def update_feedback(self, inputs: dict, result: float):
    for threshold in self.thresholds:
      threshold_value = threshold.get('value')
      if callable(threshold_value):
        threshold_value = threshold_value(inputs)
      if result >= threshold_value:
        self.set_feedback(threshold.get('text'))
        set_style(self, threshold.get('style'))
    self.update_info_dialog(inputs)

  def update_info_dialog(self, inputs: dict):
    # Clearing old rows
    for row in self.rows:
      self.thresholds_group.remove(row)
      del row
    self.rows = []
    # Creating new rows
    for threshold in self.thresholds:
      row = Adw.ActionRow()
      feedback = threshold.get('text')
      set_style(row, threshold.get('style'))
      if threshold == self.thresholds[0]:
        threshold_value = self.thresholds[1].get('value')
        text = f"Under threshold_value is {feedback}"
      else:
        threshold_value = threshold.get('value')
        text = f"threshold_value and over is {feedback}"
      if callable(threshold_value):
        threshold_value = round(threshold_value(inputs), 2)
      text = text.replace('threshold_value', str(threshold_value))
      row.set_title(text)
      self.thresholds_group.add(row)
      self.rows.append(row)

  def set_tooltip(self, tooltip: str):
    self.set_tooltip_text(tooltip)

  def get_value(self):
    try:
      return float(self.label.get_label())
    # In case label is not a number
    except ValueError:
      return self.label.get_label()

  def set_callback(self, callback):
    self.callback = callback

  def on_row_clicked(self, row):
    if self.callback is not None:
      self.callback(row)

  def on_info_button(self, button):
    self.info_dialog.set_title(f"{self.get_title()} {_('Info')}")
    self.thresholds_group.set_title(f"{self.get_title()} {_('Thresholds')}")
    self.info_dialog.present(self.get_root())
