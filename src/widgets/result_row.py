# Imports
from gi.repository import Gtk, Adw

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_row.ui')
class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'

  # Important widgets
  label = Gtk.Template.Child()
  # info_button = Gtk.Template.Child()
  # info_dialog = Gtk.Template.Child()
  # info_page = Gtk.Template.Child()

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_style(0)
    self.connect("activated", self.on_row_clicked)
    # self.info_button.connect('clicked', self.on_info_button)
    self.callback = None

  def set_feedback(self, subtitle: str):
    self.set_subtitle(subtitle)

  def set_result(self, result: str, digits: int, inputs: dict, thresholds: dict):
    if type(result) is str:
      self.label.set_label(result)
      self.set_feedback('')
      self.set_style(None)
      return
    result = round(result, digits)
    self.label.set_label(str(result))
    # Setting feedback result
    for threshold in thresholds:
      threshold_value = threshold.get('value')
      if callable(threshold_value):
        threshold_value = threshold_value(inputs)
      if result >= threshold_value:
        text = threshold.get('text')
        style = threshold.get('style')
        self.set_feedback(text)
        self.set_style(style)

  def set_tooltip(self, tooltip: str):
    self.set_tooltip_text(tooltip)

  def set_style(self, style):
    self.remove_css_class("light-blue")
    self.remove_css_class("success")
    self.remove_css_class("warning")
    self.remove_css_class("error")
    if style is None:
      return
    if style == 0:   self.add_css_class('light-blue')
    elif style == 1: self.add_css_class('success')
    elif style == 2: self.add_css_class('warning')
    elif style == 3: self.add_css_class('error')
    else:
      print(f"Unhandled style '{style}'")
      exit(-1)

  def get_value(self):
    return float(self.label.get_label())

  def set_callback(self, callback):
    self.callback = callback

  def on_row_clicked(self, row):
    if self.callback is not None:
      self.callback(row)

  # def on_info_button(self, button):
  #   self.info_dialog.present(self.get_root())
