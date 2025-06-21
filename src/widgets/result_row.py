from gi.repository import Gtk, Adw

class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Configuring row
    self.label = Gtk.Label(label='0.0')
    self.label.set_css_classes(["title-3"])
    self.add_suffix(self.label)
    self.add_css_class("heading")
    self.set_style(0)
    self.set_activatable(True)
    self.connect("activated", self.on_row_clicked)
    # Object values
    self.callback = None

  def set_feedback(self, subtitle: str):
    self.set_subtitle(subtitle)

  def set_result(self, result: str, digits: int):
    result = round(result, digits)
    self.label.set_label(str(result))

  def set_tooltip(self, tooltip: str):
    self.set_tooltip_text(tooltip)

  def set_style(self, style: int):
    self.remove_css_class("light-blue")
    self.remove_css_class("success")
    self.remove_css_class("warning")
    self.remove_css_class("error")
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
