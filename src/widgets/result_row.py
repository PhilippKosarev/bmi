# Imports
from gi.repository import GObject, Gtk, Adw

# Useful vars
styles = [
  'light-blue',
  'success',
  'warning',
  'error',
]

# Helper functions
def set_style(widget: Gtk.Widget, style_index: int):
  for style in styles:
    widget.remove_css_class(style)
  if style_index is not None:
    widget.add_css_class(styles[style_index])

@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_row.ui')
class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'

  # Widgets
  label = Gtk.Template.Child()
  info_button = Gtk.Template.Child()
  info_dialog = Gtk.Template.Child()
  info_page = Gtk.Template.Child()
  thresholds_group = Gtk.Template.Child()

  # Properties
  digits = GObject.Property(type=int, default=0)

  # rows = []

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # self.info_button.connect('clicked', self.on_info_button)

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

  # def update_info_dialog(self, inputs: dict):
  #   Clearing old rows
  #   for row in self.rows:
  #     self.thresholds_group.remove(row)
  #     del row
  #   self.rows = []
  #   Creating new rows
  #   for threshold in self.thresholds:
  #     row = Adw.ActionRow()
  #     feedback = threshold.get('text')
  #     set_style(row, threshold.get('style'))
  #     if threshold == self.thresholds[0]:
  #       threshold_value = self.thresholds[1].get('value')
  #       text = f"Under threshold_value is {feedback}"
  #     else:
  #       threshold_value = threshold.get('value')
  #       text = f"threshold_value and over is {feedback}"
  #     if callable(threshold_value):
  #       threshold_value = round(threshold_value(inputs), 2)
  #     text = text.replace('threshold_value', str(threshold_value))
  #     row.set_title(text)
  #     self.thresholds_group.add(row)
  #     self.rows.append(row)

  # def on_info_button(self, button):
  #   self.info_dialog.set_title(f"{self.get_title()} {_('Info')}")
  #   self.thresholds_group.set_title(f"{self.get_title()} {_('Thresholds')}")
  #   self.info_dialog.present(self.get_root())
